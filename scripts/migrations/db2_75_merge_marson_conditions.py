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
   appending _deleted_DB2-75. Aliases are unique across all objects, so the sources
   have to release the original names before the merged condition can take them.
4. Add the original aliases to the merged condition, after MERGED_ALIAS.

This order means a biosample always links current conditions, never a
deleted one. Biosamples are found through the search index, which can lag, so
--apply also needs --expected-biosamples, the number of biosamples linking the
4 sources. Take it from outside the index, such as the 48 Marson tissues counted
in production for DB2-75; a count copied from a dry run on a lagging index
would not catch what the index misses. The run stops before
step 1 unless the biosamples linking the sources or the merged condition add
up to it. Before step 3 it reads the biosamples again from the database, and
deletes no source while any still links one or while fewer than expected link
the merged condition. It also stops before step 1 if another object already
holds a renamed alias. With --apply the run ends with the Release A acceptance report:
no biosample links more than one ExperimentalCondition or a deleted one.
Running the script again after it has finished writes nothing and repeats
the report, but only until Release B.

This script was run on production on 2026-10-20 (DB2-75 Release A). It
applies only before Release B (Biosample schema version 5), which replaces
`experimental_conditions` with a single `experimental_condition`; after that
it finds no biosamples to repoint and stops at the --expected-biosamples
check without writing.

Credentials come from {MODE}_KEY, {MODE}_SECRET and {MODE}_SERVER, the same
convention db2-flattener uses.

Dry run by default; pass --apply to write. Progress is recorded in a state
file after every write, so an interrupted run can be resumed by running the
same command again.

    STAGING_KEY=... STAGING_SECRET=... STAGING_SERVER=https://api.staging.lattice-data.org \\
        python scripts/migrations/db2_75_merge_marson_conditions.py --mode staging
    python scripts/migrations/db2_75_merge_marson_conditions.py --mode staging --apply --expected-biosamples 48
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
# Not plain _deleted: DB2-74 gave the deleted Treatments these same aliases with that suffix.
DELETED_ALIAS_SUFFIX = '_deleted_DB2-75'

TIME_POINT_PROPERTIES = ('lower_bound_time_point', 'upper_bound_time_point', 'time_point_units')

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

    def find_by_alias(self, alias, collection='/experimental_conditions'):
        """Return the object with this alias, or None.

        Aliases resolve through the database's unique keys, not the search index, so an
        object is found as soon as its POST commits. Pass collection='' to look the alias
        up from the root, which searches every type; aliases are unique across all of them.
        """
        path = f'{collection}/{alias}/?frame=object&format=json&datastore=database'
        response = self.session.get(self.server + path)
        if response.status_code == 404:
            return None
        if not response.ok:
            raise RuntimeError(f'GET {path} failed with {response.status_code}: {response.text}')
        return response.json()

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
    run reads the sources from state instead of looking them up.
    """
    if 'sources' in state:
        return [state['sources'][alias] for alias in SOURCE_ALIASES]
    sources = {}
    for alias in SOURCE_ALIASES:
        condition = client.find_by_alias(alias)
        if condition is None:
            raise RuntimeError(f'no ExperimentalCondition has alias {alias}.')
        sources[alias] = condition['@id']
    state['sources'] = sources
    return [sources[alias] for alias in SOURCE_ALIASES]


def check_source(condition, alias):
    """Fail unless the condition is a schema 3 single-term Marson condition with only this alias.

    Step 3 replaces the aliases with the renamed one, so a second alias would be lost.
    """
    condition_id = condition['@id']
    if condition.get('aliases') not in ([alias], [f'{alias}{DELETED_ALIAS_SUFFIX}']):
        raise RuntimeError(f'{condition_id} has aliases {condition.get("aliases")}, expected only {alias}.')
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


def check_biosample_count(count, expected_biosamples, what):
    if expected_biosamples is not None and count != expected_biosamples:
        raise RuntimeError(
            f'{count} biosample(s) {what}, expected {expected_biosamples}. The search may be missing '
            'biosamples the index has not caught up with; wait for indexing and run again.'
        )


def acceptance_report(client, state, expected_biosamples=None):
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
    if expected_biosamples is not None:
        checks.append((
            f'{expected_biosamples} biosample(s) link the merged condition',
            [] if linking_merged == expected_biosamples else [f'{linking_merged} found'],
        ))
    print(f'Acceptance report for {client.server}')
    print(f'  Merged condition {merged_id}: {merged.get("summary")}')
    print(f'  {linking_merged} biosample(s) link it; {len(biosamples)} biosample(s) link any ExperimentalCondition')
    for title, failures in checks:
        print(f'  {"PASS" if not failures else "FAIL"}: {title}')
        for failure in failures:
            print(f'      {failure}')
    return not any(failures for _, failures in checks)


def find_existing_merged(client, item):
    """Return the @id of a merged condition an earlier run created but did not record, or None.

    The POST can commit even when the run dies before saving state, for example on a
    dropped connection. Posting again would fail on the MERGED_ALIAS unique key.
    """
    existing = client.find_by_alias(MERGED_ALIAS, collection='')
    if existing is None:
        return None
    if existing.get('lab') != item['lab'] or existing.get('controlled_terms') != item['controlled_terms']:
        raise RuntimeError(
            f'{existing["@id"]} already has alias {MERGED_ALIAS} but does not match the merged condition: '
            f'lab {existing.get("lab")}, controlled_terms {existing.get("controlled_terms")}.'
        )
    return existing['@id']


def check_renamed_aliases_free(client, sources):
    """Fail unless each renamed alias is unused or already belongs to its source.

    Step 3 would otherwise stop with a 409 after the biosamples have been repointed.
    """
    taken = []
    for alias, source in zip(SOURCE_ALIASES, sources):
        renamed_alias = f'{alias}{DELETED_ALIAS_SUFFIX}'
        holder = client.find_by_alias(renamed_alias, collection='')
        if holder is not None and holder['@id'] != source['@id']:
            taken.append(f'{renamed_alias} is held by {holder["@id"]}')
    if taken:
        raise RuntimeError(
            'renamed aliases are already taken, so step 3 would fail; nothing was written:\n    '
            + '\n    '.join(taken)
        )


def merge(client, state, state_path, expected_biosamples=None):
    source_ids = find_sources(client, state)
    save_state(state_path, state, client.apply)
    sources = [client.get_object(source_id) for source_id in source_ids]
    for alias, source in zip(SOURCE_ALIASES, sources):
        check_source(source, alias)
    check_renamed_aliases_free(client, sources)
    for alias, source in zip(SOURCE_ALIASES, sources):
        print(f'Source {source["@id"]} ({alias}): {source.get("summary")}')
    biosamples = read_biosamples(client, state.get('biosamples', []))
    to_repoint = find_biosamples_to_repoint(biosamples, source_ids)
    already = [
        biosample_id for biosample_id, biosample in biosamples.items()
        if state.get('merged') and biosample.get('experimental_conditions') == [state['merged']]
    ]
    print(
        f'{len(biosamples)} biosample(s) link an ExperimentalCondition; {len(to_repoint)} link the 4 sources'
        + (f', {len(already)} the merged condition' if already else '')
    )
    check_biosample_count(len(to_repoint) + len(already), expected_biosamples,
                          'link the 4 sources or the merged condition')

    # Step 1: create the merged ExperimentalCondition.
    merged_id = state.get('merged')
    item = build_merged(sources)
    if not merged_id:
        merged_id = find_existing_merged(client, item)
        if merged_id:
            state['merged'] = merged_id
            save_state(state_path, state, client.apply)
    if merged_id:
        print(f'1. Merged ExperimentalCondition already created: {merged_id}')
    else:
        created = client.write('POST', '/experimental_conditions/', item)
        if created is None:
            merged_id = '<merged experimental condition>'
        else:
            merged_id = created['@id']
            state['merged'] = merged_id
            save_state(state_path, state, client.apply)
        print(f'1. Created merged ExperimentalCondition {merged_id}')

    # Step 2: repoint biosamples.
    print(f'2. Repointing {len(to_repoint)} biosample(s); {len(already)} already repointed')
    for biosample_id in to_repoint:
        client.write('PATCH', biosample_id, {'experimental_conditions': [merged_id]})
        print(f'   {biosample_id}: repointed')
        state.setdefault('biosamples', [])
        if biosample_id not in state['biosamples']:
            state['biosamples'].append(biosample_id)
            save_state(state_path, state, client.apply)

    # Step 3: delete the sources and release their aliases by renaming them. Read the
    # biosamples again first, so a source is never deleted while something links it.
    if client.apply:
        biosamples = read_biosamples(client, state.get('biosamples', []))
        still_linking = [
            biosample_id for biosample_id, biosample in biosamples.items()
            if set(biosample.get('experimental_conditions', [])) & set(source_ids)
        ]
        if still_linking:
            raise RuntimeError(
                f'{len(still_linking)} biosample(s) still link a source condition, so none was deleted: '
                f'{", ".join(still_linking)}. Run again to repoint them.'
            )
        linking_merged = sum(
            merged_id in biosample.get('experimental_conditions', []) for biosample in biosamples.values()
        )
        check_biosample_count(linking_merged, expected_biosamples, 'link the merged condition')
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
    parser.add_argument('--expected-biosamples', type=int,
                        help='How many biosamples link the 4 source conditions (48 in production). Required with '
                             '--apply: the run stops before step 1 and again before step 3 unless the count matches.')
    args = parser.parse_args()
    if args.apply and args.expected_biosamples is None:
        parser.error('--apply needs --expected-biosamples: the number of Marson tissues known to link the 4 '
                     'sources (48 in production), not a count read back from the dry run.')

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
        merge(client, state, state_path, args.expected_biosamples)
        if args.apply:
            print(f'State written to {state_path}')
            if not acceptance_report(client, state, args.expected_biosamples):
                sys.exit(1)
    except RuntimeError as error:
        print(f'FAILED: {error}')
        sys.exit(1)


if __name__ == '__main__':
    main()
