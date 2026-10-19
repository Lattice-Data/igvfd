"""DB2-75 Release A: merge the 4 Marson ExperimentalConditions into one.

Run only after ExperimentalCondition schema version 3 (controlled_terms and the
time point range) is deployed to the target server.

The Marson tissues each link the same 4 single-term protein treatment
conditions. This script replaces them with one condition carrying all 4 terms.

Before any write it reads every biosample that links an ExperimentalCondition
and stops unless each one links exactly the 4 source conditions, a single other
condition, or none. Any other pattern (some of the sources, the sources plus
another condition, several other conditions) is listed and needs a decision
this script does not make. Then:

1. POST the merged ExperimentalCondition with the 4 controlled terms in
   SOURCE_ALIASES order, the shared time point and MERGED_ALIAS.
2. Repoint every biosample that links the 4 source conditions to the merged
   condition alone.
3. Set each source condition to status deleted and rename its aliases by
   appending _deleted. Aliases are unique across all objects, so the sources
   have to release the original names before the merged condition can take them.
4. Add the original aliases to the merged condition, after MERGED_ALIAS.

This order means a biosample always links current conditions, never a
deleted one. With --apply the run ends with the Release A acceptance report:
no biosample links more than one ExperimentalCondition or a deleted one.
Running the script again after it has finished writes nothing and repeats
the report.

Credentials come from {MODE}_KEY, {MODE}_SECRET and {MODE}_SERVER, the same
convention db2-flattener uses.

Dry run by default; pass --apply to write. Progress is recorded in a state
file after every write, so an interrupted run can be resumed by running the
same command again.

    STAGING_KEY=... STAGING_SECRET=... STAGING_SERVER=https://api.staging.lattice-data.org \\
        python scripts/migrations/db2_75_merge_marson_conditions.py --mode staging
    python scripts/migrations/db2_75_merge_marson_conditions.py --mode staging --apply
"""
import argparse
import json
import os
import sys
from pathlib import Path

import requests


# The source conditions, in the order their terms appear on the merged condition.
SOURCE_ALIASES = (
    'alex-marson:treatment_anti-CD3E_human',
    'alex-marson:treatment_anti-CD28_human',
    'alex-marson:treatment_anti-CD2_human',
    'alex-marson:treatment_IL2_human',
)

# Marks the merged condition; the 4 source aliases are added after it in step 4.
MERGED_ALIAS = 'alex-marson:stimulation_anti-CD3E_anti-CD28_anti-CD2_IL2_human_merged'

LAB = '/labs/alex-marson/'

# Appended to a deleted source condition's aliases so the merged condition can take the originals.
DELETED_ALIAS_SUFFIX = '_deleted'

TIME_POINT_PROPERTIES = ('lower_bound_time_point', 'upper_bound_time_point', 'time_point_units')

CONDITION_SEARCH = (
    '/search/?type=ExperimentalCondition&aliases={alias}'
    '&status=current&status=deleted&field=@id&limit=all&format=json'
)

BIOSAMPLE_SEARCH = (
    '/search/?type=Biosample&experimental_conditions=*'
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
        # behind writes.
        separator = '&' if '?' in path else '?'
        return self._request('GET', f'{path}{separator}format=json&datastore=database')

    def get_object(self, path):
        return self.get(f'{path}?frame=object')

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


def find_sources(client, state):
    """Return the source condition @ids in SOURCE_ALIASES order, recording them in state.

    Once step 4 has run, the original aliases name the merged condition, so a resumed
    run reads the sources from state instead of searching.
    """
    if 'sources' in state:
        return [state['sources'][alias] for alias in SOURCE_ALIASES]
    sources = {}
    for alias in SOURCE_ALIASES:
        hits = client.search(CONDITION_SEARCH.format(alias=alias))
        if len(hits) != 1:
            raise RuntimeError(f'expected 1 ExperimentalCondition with alias {alias}, found {len(hits)}.')
        sources[alias] = hits[0]['@id']
    state['sources'] = sources
    return [sources[alias] for alias in SOURCE_ALIASES]


def check_source(condition):
    """Fail unless the condition is a schema 3 single-term Marson condition."""
    condition_id = condition['@id']
    if condition.get('schema_version') != '3':
        raise RuntimeError(
            f'{condition_id} is at schema_version {condition.get("schema_version")}; '
            'deploy ExperimentalCondition schema version 3 first.'
        )
    if condition.get('lab') != LAB:
        raise RuntimeError(f'{condition_id} belongs to {condition.get("lab")}, expected {LAB}.')
    if len(condition.get('controlled_terms', [])) != 1:
        raise RuntimeError(
            f'{condition_id} has {len(condition.get("controlled_terms", []))} controlled_terms, expected 1.')


def build_merged(sources):
    time_points = {tuple(source.get(name) for name in TIME_POINT_PROPERTIES) for source in sources}
    if len(time_points) != 1:
        raise RuntimeError(f'source conditions disagree on the time point: {sorted(map(str, time_points))}.')
    item = {
        'lab': LAB,
        'controlled_terms': [source['controlled_terms'][0] for source in sources],
        'aliases': [MERGED_ALIAS],
        'notes': (
            f'Merged from ExperimentalConditions {", ".join(source["@id"] for source in sources)} (DB2-75).'
        ),
    }
    for name, value in zip(TIME_POINT_PROPERTIES, time_points.pop()):
        if value is not None:
            item[name] = value
    return item


def read_biosamples(client, extra_ids=()):
    """Read every biosample that links an ExperimentalCondition from the database.

    The search only finds them; each is then read with datastore=database so the
    links are current. extra_ids adds biosamples the index may not show yet.
    """
    biosample_ids = {hit['@id'] for hit in client.search(BIOSAMPLE_SEARCH)} | set(extra_ids)
    return {biosample_id: client.get_object(biosample_id) for biosample_id in sorted(biosample_ids)}


def find_biosamples_to_repoint(biosamples, source_ids):
    """Return the biosamples linking exactly the source conditions.

    Fail, listing them, if any biosample links more than one condition in another
    combination, or a single source condition on its own.
    """
    to_repoint = []
    unexpected = []
    for biosample_id, biosample in biosamples.items():
        links = biosample.get('experimental_conditions', [])
        if sorted(links) == sorted(source_ids):
            to_repoint.append(biosample_id)
        elif len(links) > 1 or set(links) & set(source_ids):
            unexpected.append(f'{biosample_id} ({biosample.get("status")}): {", ".join(links)}')
    if unexpected:
        raise RuntimeError(
            f'{len(unexpected)} biosample(s) link ExperimentalConditions in a pattern this script does not handle; '
            'nothing was written:\n    ' + '\n    '.join(unexpected)
        )
    return to_repoint


def acceptance_report(client, state):
    """Print the Release A acceptance checks and return whether they all pass."""
    merged_id = state['merged']
    biosamples = read_biosamples(client, state.get('biosamples', []))
    statuses = {}
    multiple = []
    deleted_links = []
    for biosample_id, biosample in biosamples.items():
        links = biosample.get('experimental_conditions', [])
        if len(links) > 1:
            multiple.append(f'{biosample_id}: {", ".join(links)}')
        for link in links:
            if link not in statuses:
                statuses[link] = client.get_object(link)['status']
            if statuses[link] == 'deleted':
                deleted_links.append(f'{biosample_id} -> {link}')
    merged = client.get_object(merged_id)
    sources = [client.get_object(source_id) for source_id in state['sources'].values()]
    linking_merged = sum(merged_id in biosample.get('experimental_conditions', []) for biosample in biosamples.values())
    checks = [
        ('No biosample links more than one ExperimentalCondition', multiple),
        ('No biosample links a deleted ExperimentalCondition', deleted_links),
        ('Source conditions are deleted', [source['@id'] for source in sources if source['status'] != 'deleted']),
        ('Merged condition has MERGED_ALIAS and the source aliases',
         [] if merged.get('aliases') == [MERGED_ALIAS] + list(SOURCE_ALIASES) else [str(merged.get('aliases'))]),
    ]
    print(f'Acceptance report for {client.server}')
    print(f'  Merged condition {merged_id}: {merged.get("summary")}')
    print(f'  {linking_merged} biosample(s) link it; {len(biosamples)} biosample(s) link any ExperimentalCondition')
    for title, failures in checks:
        print(f'  {"PASS" if not failures else "FAIL"}: {title}')
        for failure in failures:
            print(f'      {failure}')
    return not any(failures for _, failures in checks)


def merge(client, state, state_path):
    source_ids = find_sources(client, state)
    save_state(state_path, state, client.apply)
    sources = [client.get_object(source_id) for source_id in source_ids]
    for source in sources:
        check_source(source)
    for alias, source in zip(SOURCE_ALIASES, sources):
        print(f'Source {source["@id"]} ({alias}): {source.get("summary")}')
    biosamples = read_biosamples(client, state.get('biosamples', []))
    to_repoint = find_biosamples_to_repoint(biosamples, source_ids)
    print(f'{len(biosamples)} biosample(s) link an ExperimentalCondition; {len(to_repoint)} link the 4 sources')

    # Step 1: create the merged ExperimentalCondition.
    merged_id = state.get('merged')
    if merged_id:
        print(f'1. Merged ExperimentalCondition already created: {merged_id}')
    else:
        created = client.write('POST', '/experimental_conditions/', build_merged(sources))
        if created is None:
            merged_id = '<merged experimental condition>'
        else:
            merged_id = created['@id']
            state['merged'] = merged_id
            save_state(state_path, state, client.apply)
        print(f'1. Created merged ExperimentalCondition {merged_id}')

    # Step 2: repoint biosamples.
    already = sum(biosample.get('experimental_conditions') == [merged_id] for biosample in biosamples.values())
    print(f'2. Repointing {len(to_repoint)} biosample(s); {already} already repointed')
    for biosample_id in to_repoint:
        client.write('PATCH', biosample_id, {'experimental_conditions': [merged_id]})
        print(f'   {biosample_id}: repointed')
        state.setdefault('biosamples', [])
        if biosample_id not in state['biosamples']:
            state['biosamples'].append(biosample_id)
            save_state(state_path, state, client.apply)

    # Step 3: delete the sources and release their aliases by renaming them.
    print('3. Deleting source conditions')
    for alias, source in zip(SOURCE_ALIASES, sources):
        renamed_alias = f'{alias}{DELETED_ALIAS_SUFFIX}'
        if source['status'] == 'deleted' and source.get('aliases') == [renamed_alias]:
            print(f'   {source["@id"]}: already deleted')
            continue
        note = (
            f'Merged into {merged_id} during DB2-75. Alias renamed with {DELETED_ALIAS_SUFFIX}; '
            f'the original {alias} moved to {merged_id}.'
        )
        client.write('PATCH', source['@id'], {
            'status': 'deleted',
            'aliases': [renamed_alias],
            'notes': append_note(source.get('notes'), note),
        })
        print(f'   {source["@id"]}: set to deleted, alias renamed to {renamed_alias}')

    # Step 4: give the merged condition the original aliases.
    aliases = [MERGED_ALIAS] + list(SOURCE_ALIASES)
    if client.apply and client.get_object(merged_id).get('aliases') == aliases:
        print('4. Aliases already moved')
    else:
        client.write('PATCH', merged_id, {'aliases': aliases})
        print(f'4. Set aliases on {merged_id}: {", ".join(aliases)}')
    state['done'] = True
    save_state(state_path, state, client.apply)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--mode', required=True,
                        help='Credential prefix, e.g. staging reads STAGING_KEY, STAGING_SECRET, STAGING_SERVER.')
    parser.add_argument('--apply', action='store_true',
                        help='Write changes. Without it the script only prints what it would do.')
    parser.add_argument('--state-file', type=Path,
                        help='Progress file. Default: db2_75_merge_marson_conditions_<mode>.json in the current directory.')
    args = parser.parse_args()

    prefix = args.mode.upper()
    missing = [f'{prefix}_{name}' for name in ('KEY', 'SECRET', 'SERVER') if not os.environ.get(f'{prefix}_{name}')]
    if missing:
        parser.error(f'missing environment variables: {", ".join(missing)}')
    client = Client(os.environ[f'{prefix}_SERVER'], os.environ[f'{prefix}_KEY'],
                    os.environ[f'{prefix}_SECRET'], args.apply)
    state_path = args.state_file or Path(f'db2_75_merge_marson_conditions_{args.mode}.json')
    state = load_state(state_path)

    print(f'{"Applying" if args.apply else "Dry run"} against {client.server}')
    try:
        merge(client, state, state_path)
        if args.apply:
            print(f'State written to {state_path}')
            if not acceptance_report(client, state):
                sys.exit(1)
    except RuntimeError as error:
        print(f'FAILED: {error}')
        sys.exit(1)


if __name__ == '__main__':
    main()
