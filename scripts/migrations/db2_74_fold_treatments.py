"""DB2-74 stage 2: fold Treatment objects into ExperimentalCondition.

Run only after DB2-74 stage 1 (chemical treatment / protein treatment
conditions on ExperimentalCondition) is deployed to the target server.

For each Treatment that is not already deleted:

1. POST an equivalent ExperimentalCondition, without aliases.
2. Repoint every biosample that links the Treatment: add the new
   ExperimentalCondition to experimental_conditions and drop the Treatment
   from treatments.
3. Set the Treatment to status deleted and rename its aliases by appending
   _deleted. Aliases are unique across all objects, so the Treatment has to
   release the original names before the new object can take them.
4. Add the Treatment's original aliases to the new ExperimentalCondition.

This order means a biosample always links either the Treatment or its
replacement, never a deleted object.

Credentials come from {MODE}_KEY, {MODE}_SECRET and {MODE}_SERVER, the same
convention db2-flattener uses. Use an admin key: biosamples left with no
treatments are PUT from their @@edit view, which includes server-managed
fields.

Dry run by default; pass --apply to write. Progress is recorded in a state
file after every write, so an interrupted run can be resumed by running the
same command again.

    STAGING_KEY=... STAGING_SECRET=... STAGING_SERVER=https://api.staging.lattice-data.org \\
        python scripts/migrations/db2_74_fold_treatments.py --mode staging
    python scripts/migrations/db2_74_fold_treatments.py --mode staging --apply
"""
import argparse
import json
import os
import sys
from pathlib import Path

import requests


CONDITION_BY_ONTOLOGY_SOURCE = {
    'CHEBI': 'chemical treatment',
    'UniProt': 'protein treatment',
}

# Treatment.amount_units values that are spelled differently in ExperimentalCondition.units.
UNITS_RENAMES = {
    'kpa': 'kPa',
}

# Appended to a deleted Treatment's aliases so the new ExperimentalCondition can take the originals.
DELETED_ALIAS_SUFFIX = '_deleted'

# Treatment properties copied unchanged onto the new ExperimentalCondition.
COPIED_PROPERTIES = (
    'lab',
    'description',
    'submitter_comment',
    'lower_bound_duration',
    'upper_bound_duration',
    'duration_units',
)

BIOSAMPLE_SEARCH = (
    '/search/?type=Biosample&treatments.@id={treatment_id}'
    '&status=current&status=deleted&field=@id&limit=all&format=json'
)


class Client:

    def __init__(self, server, key, secret, apply):
        self.server = server.rstrip('/')
        self.apply = apply
        self.session = requests.Session()
        self.session.auth = (key, secret)
        self.session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})

    def _request(self, method, path, body=None):
        response = self.session.request(method, self.server + path, data=None if body is None else json.dumps(body))
        if not response.ok:
            raise RuntimeError(f'{method} {path} failed with {response.status_code}: {response.text}')
        return response.json()

    def get(self, path):
        # Without datastore=database GETs can be served from the search index, which lags
        # behind writes. A biosample linking two Treatments would then be PATCHed from a
        # stale copy, undoing the first repoint.
        separator = '&' if '?' in path else '?'
        return self._request('GET', f'{path}{separator}format=json&datastore=database')

    def get_object(self, path):
        return self.get(f'{path}?frame=object')

    def get_edit(self, path):
        return self.get(f'{path.rstrip("/")}/@@edit')

    def search(self, path):
        response = self.session.get(self.server + path)
        # snovault answers an empty search with 404.
        if response.status_code == 404:
            return []
        if not response.ok:
            raise RuntimeError(f'GET {path} failed with {response.status_code}: {response.text}')
        return response.json()['@graph']

    def write(self, method, path, body):
        if not self.apply:
            print(f'    [dry run] {method} {path} {json.dumps(body, ensure_ascii=False, sort_keys=True)}')
            return None
        result = self._request(method, path, body)
        return result['@graph'][0]


def load_state(path):
    if path.exists():
        return json.loads(path.read_text())
    return {}


def save_state(path, state, apply):
    if apply:
        path.write_text(json.dumps(state, indent=4, sort_keys=True) + '\n')


def append_note(existing, note):
    return f'{existing}\n{note}' if existing else note


def build_condition(client, treatment):
    term_id = treatment['ontological_term']
    term = client.get_object(term_id)
    source = term.get('ontology_source')
    condition = CONDITION_BY_ONTOLOGY_SOURCE.get(source)
    if condition is None:
        raise RuntimeError(
            f'{treatment["@id"]} has ontological_term {term_id} with ontology_source {source!r}; '
            f'expected one of {sorted(CONDITION_BY_ONTOLOGY_SOURCE)}.'
        )
    item = {
        'condition': condition,
        'controlled_term': term_id,
        'status': treatment['status'],
        'notes': append_note(treatment.get('notes'), f'Migrated from Treatment {treatment["@id"]} (DB2-74).'),
    }
    for name in COPIED_PROPERTIES:
        if name in treatment:
            item[name] = treatment[name]
    if 'amount' in treatment:
        item['value'] = treatment['amount']
        item['units'] = UNITS_RENAMES.get(treatment['amount_units'], treatment['amount_units'])
    return item


def put_from_edit(client, path, drop, updates):
    """PUT an item back from its @@edit view, so properties can be removed as well as set."""
    edit = client.get_edit(path)
    item_type = client.get_object(path)['@type'][0]
    allowed = client.get(f'/profiles/{item_type}.json')['properties']
    body = {name: value for name, value in edit.items() if name in allowed and name not in drop}
    body.update(updates)
    return client.write('PUT', path, body)


def migrate_treatment(client, treatment_id, state, state_path):
    treatment = client.get_object(treatment_id)
    record = state.setdefault(treatment['uuid'], {'treatment': treatment_id})
    record.setdefault('aliases', treatment.get('aliases', []))
    print(f'{treatment_id} ({", ".join(record["aliases"]) or "no aliases"})')

    # Step 1: create the replacement ExperimentalCondition.
    condition_id = record.get('experimental_condition')
    if condition_id:
        print(f'  1. ExperimentalCondition already created: {condition_id}')
    else:
        item = build_condition(client, treatment)
        created = client.write('POST', '/experimental_conditions/', item)
        if created is None:
            condition_id = '<new experimental condition>'
        else:
            condition_id = created['@id']
            record['experimental_condition'] = condition_id
            save_state(state_path, state, client.apply)
        print(f'  1. Created ExperimentalCondition {condition_id}')

    # Step 2: repoint biosamples.
    biosample_ids = sorted(hit['@id'] for hit in client.search(BIOSAMPLE_SEARCH.format(treatment_id=treatment_id)))
    biosample_ids = sorted(set(biosample_ids) | set(record.get('biosamples', [])))
    print(f'  2. Repointing {len(biosample_ids)} biosample(s)')
    for biosample_id in biosample_ids:
        biosample = client.get_object(biosample_id)
        treatments = biosample.get('treatments', [])
        conditions = biosample.get('experimental_conditions', [])
        if treatment_id not in treatments and condition_id in conditions:
            print(f'     {biosample_id}: already repointed')
            continue
        new_conditions = conditions if condition_id in conditions else conditions + [condition_id]
        new_treatments = [link for link in treatments if link != treatment_id]
        if new_treatments:
            client.write('PATCH', biosample_id, {
                'experimental_conditions': new_conditions,
                'treatments': new_treatments,
            })
        else:
            put_from_edit(client, biosample_id, drop={'treatments'}, updates={
                'experimental_conditions': new_conditions,
            })
        print(f'     {biosample_id}: repointed')
        record.setdefault('biosamples', [])
        if biosample_id not in record['biosamples']:
            record['biosamples'].append(biosample_id)
            save_state(state_path, state, client.apply)

    # Step 3: delete the Treatment and release its aliases by renaming them.
    renamed_aliases = [f'{alias}{DELETED_ALIAS_SUFFIX}' for alias in record['aliases']]
    if treatment['status'] == 'deleted' and treatment.get('aliases', []) == renamed_aliases:
        print('  3. Treatment already deleted')
    else:
        updates = {'status': 'deleted'}
        if renamed_aliases:
            updates['aliases'] = renamed_aliases
            note = (
                f'Aliases renamed with {DELETED_ALIAS_SUFFIX} during DB2-74 migration; '
                f'the originals moved to {condition_id}: {", ".join(record["aliases"])}.'
            )
            updates['notes'] = append_note(treatment.get('notes'), note)
        client.write('PATCH', treatment_id, updates)
        print(f'  3. Treatment set to deleted, aliases renamed with {DELETED_ALIAS_SUFFIX}')

    # Step 4: give the new ExperimentalCondition the original aliases.
    if not record['aliases']:
        print('  4. No aliases to move')
    elif client.apply and client.get_object(condition_id).get('aliases') == record['aliases']:
        print('  4. Aliases already moved')
    else:
        client.write('PATCH', condition_id, {'aliases': record['aliases']})
        print(f'  4. Added aliases {", ".join(record["aliases"])} to {condition_id}')
    record['done'] = True
    save_state(state_path, state, client.apply)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--mode', required=True,
                        help='Credential prefix, e.g. staging reads STAGING_KEY, STAGING_SECRET, STAGING_SERVER.')
    parser.add_argument('--apply', action='store_true',
                        help='Write changes. Without it the script only prints what it would do.')
    parser.add_argument('--treatment', action='append', default=[], help='Migrate only this Treatment @id. Repeatable.')
    parser.add_argument('--state-file', type=Path,
                        help='Progress file. Default: db2_74_fold_treatments_<mode>.json in the current directory.')
    args = parser.parse_args()

    prefix = args.mode.upper()
    missing = [f'{prefix}_{name}' for name in ('KEY', 'SECRET', 'SERVER') if not os.environ.get(f'{prefix}_{name}')]
    if missing:
        parser.error(f'missing environment variables: {", ".join(missing)}')
    client = Client(os.environ[f'{prefix}_SERVER'], os.environ[f'{prefix}_KEY'],
                    os.environ[f'{prefix}_SECRET'], args.apply)
    state_path = args.state_file or Path(f'db2_74_fold_treatments_{args.mode}.json')
    state = load_state(state_path)

    if args.treatment:
        treatment_ids = args.treatment
    else:
        hits = client.search('/search/?type=Treatment&status=current&field=@id&limit=all&format=json')
        treatment_ids = sorted(hit['@id'] for hit in hits)
        # Resume Treatments a previous run already deleted but did not finish.
        treatment_ids += sorted(
            record['treatment'] for record in state.values()
            if not record.get('done') and record['treatment'] not in treatment_ids
        )

    print(f'{"Applying" if args.apply else "Dry run"} against {client.server}: {len(treatment_ids)} Treatment(s)')
    failures = []
    for treatment_id in treatment_ids:
        try:
            migrate_treatment(client, treatment_id, state, state_path)
        except RuntimeError as error:
            print(f'  FAILED: {error}')
            failures.append(treatment_id)
    if args.apply:
        print(f'State written to {state_path}')
    if failures:
        print(f'{len(failures)} Treatment(s) failed: {", ".join(failures)}')
        sys.exit(1)


if __name__ == '__main__':
    main()
