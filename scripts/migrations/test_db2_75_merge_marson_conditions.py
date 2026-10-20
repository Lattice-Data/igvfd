"""Tests for db2_75_merge_marson_conditions.py against an in-memory fake server.

The root pytest.ini collects igvfd.tests only, so run these with its addopts cleared:

    pytest -o addopts='' scripts/migrations
"""
import copy
import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

spec = importlib.util.spec_from_file_location(
    'db2_75_merge_marson_conditions',
    Path(__file__).with_name('db2_75_merge_marson_conditions.py'),
)
merge_script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(merge_script)

TERMS = [
    '/controlled_terms/anti-uniprot:P07766/',
    '/controlled_terms/anti-uniprot:P10747/',
    '/controlled_terms/anti-uniprot:P06729/',
    '/controlled_terms/uniprot:P60568/',
]
SOURCES = [f'/experimental_conditions/source{i}/' for i in range(4)]
OTHER = '/experimental_conditions/other/'
OTHER_2 = '/experimental_conditions/other2/'
TISSUES = [f'/tissues/tissue{n}/' for n in range(48)]


def make_db():
    """A small copy of production: 4 Marson sources, 48 tissues linking all 4, one Weissman tissue."""
    db = {}
    # Inserted out of order, to show the merged terms follow SOURCE_ALIASES.
    for i in (3, 0, 2, 1):
        db[SOURCES[i]] = {
            '@id': SOURCES[i],
            'schema_version': '3',
            'lab': merge_script.LAB,
            'status': 'current',
            'aliases': [merge_script.SOURCE_ALIASES[i]],
            'controlled_terms': [TERMS[i]],
            'description': 'stimulation',
            'summary': 'stimulation',
            'notes': 'Migrated from Treatment (DB2-74).',
            'lower_bound_time_point': 8,
            'upper_bound_time_point': 8,
            'time_point_units': 'hour',
        }
    # DB2-74's deleted Treatments hold the same aliases with plain _deleted, as in production.
    for i in range(4):
        treatment_id = f'/treatments/treatment{i}/'
        db[treatment_id] = {
            '@id': treatment_id,
            'status': 'deleted',
            'aliases': [f'{merge_script.SOURCE_ALIASES[i]}_deleted'],
        }
    for condition_id in (OTHER, OTHER_2):
        db[condition_id] = {
            '@id': condition_id,
            'status': 'current',
            'aliases': [f'jonathan-weissman:{condition_id.split("/")[2]}'],
        }
    for tissue_id in TISSUES:
        db[tissue_id] = {'@id': tissue_id, 'status': 'current', 'experimental_conditions': sorted(SOURCES)}
    db['/tissues/weissman/'] = {'@id': '/tissues/weissman/', 'status': 'current', 'experimental_conditions': [OTHER]}
    db['/tissues/none/'] = {'@id': '/tissues/none/', 'status': 'current', 'experimental_conditions': []}
    return db


class Crash(Exception):
    pass


class FakeClient(merge_script.Client):
    """Applies writes to db and enforces the server rules the script relies on.

    crash_after: raise before the write after that many writes, so nothing is committed.
    lose_response_after: commit the write, then raise, as when the response is lost.
    hidden: biosample @ids the search index does not return yet.
    after_write: hook called after each committed write.
    """

    def __init__(self, db, apply, crash_after=None, lose_response_after=None, hidden=(), after_write=None):
        self.server = 'fake'
        self.apply = apply
        self.db = db
        self.writes = 0
        self.crash_after = crash_after
        self.lose_response_after = lose_response_after
        self.hidden = set(hidden)
        self.after_write = after_write

    def find_by_alias(self, alias, collection='/experimental_conditions'):
        # A collection path only resolves aliases its own type holds; the root resolves any type.
        hits = [
            item for item in self.db.values()
            if alias in item.get('aliases', []) and item['@id'].startswith(f'{collection}/')
        ]
        return copy.deepcopy(hits[0]) if hits else None

    def search(self, path):
        query = parse_qs(urlparse(path).query)
        assert query['experimental_conditions'] == ['*']
        return [
            {'@id': item_id} for item_id, item in self.db.items()
            if item.get('experimental_conditions') and item_id not in self.hidden
        ]

    def _request(self, method, path, body=None):
        if method == 'GET':
            return copy.deepcopy(self.db[path.split('?')[0]])
        if self.crash_after is not None and self.writes >= self.crash_after:
            raise Crash()
        self.writes += 1
        result = self._write(method, path, body)
        if self.after_write:
            self.after_write(self)
        if self.lose_response_after is not None and self.writes > self.lose_response_after:
            raise Crash()
        return result

    def _check_aliases_free(self, path, aliases):
        for item_id, item in self.db.items():
            conflict = set(item.get('aliases', [])) & set(aliases)
            if item_id != path and conflict:
                raise RuntimeError(f'409 Keys conflict on {path}: {sorted(conflict)}')

    def _write(self, method, path, body):
        if method == 'POST':
            self._check_aliases_free(None, body['aliases'])
            new_id = f'/experimental_conditions/merged{len(self.db)}/'
            self.db[new_id] = dict(body, **{
                '@id': new_id,
                'status': 'current',
                'schema_version': '3',
                'summary': 'anti-CD3E_HUMAN, anti-CD28_HUMAN, anti-CD2_HUMAN and IL2_HUMAN, 8 hours',
            })
            return {'@graph': [self.db[new_id]]}
        assert method == 'PATCH'
        if 'aliases' in body:
            self._check_aliases_free(path, body['aliases'])
        for link in body.get('experimental_conditions', []):
            assert self.db[link]['status'] != 'deleted', f'{path} would link deleted {link}'
        if body.get('status') == 'deleted':
            for item_id, item in self.db.items():
                assert path not in item.get('experimental_conditions', []), f'{path} is still linked by {item_id}'
        self.db[path].update(body)
        return {'@graph': [self.db[path]]}


def merged_id(db):
    merged = [item_id for item_id in db if '/merged' in item_id]
    assert len(merged) == 1, merged
    return merged[0]


def assert_merged(db):
    merged = db[merged_id(db)]
    assert merged['controlled_terms'] == TERMS
    assert merged['aliases'] == [merge_script.MERGED_ALIAS] + list(merge_script.SOURCE_ALIASES)
    assert (merged['lower_bound_time_point'], merged['upper_bound_time_point'], merged['time_point_units']) == (
        8, 8, 'hour')
    assert 'description' not in merged
    for tissue_id in TISSUES:
        assert db[tissue_id]['experimental_conditions'] == [merged['@id']]
    assert db['/tissues/weissman/']['experimental_conditions'] == [OTHER]
    for i, source_id in enumerate(SOURCES):
        source = db[source_id]
        assert source['status'] == 'deleted'
        assert source['aliases'] == [f'{merge_script.SOURCE_ALIASES[i]}{merge_script.DELETED_ALIAS_SUFFIX}']
        assert source['notes'].startswith(f'Migrated from Treatment (DB2-74).\nMerged into {merged["@id"]}')
        assert db[f'/treatments/treatment{i}/']['aliases'] == [f'{merge_script.SOURCE_ALIASES[i]}_deleted']


def run(client, state_path, expected=48):
    """Run merge plus, with apply, the acceptance report; return (report passed, output)."""
    out = io.StringIO()
    with redirect_stdout(out):
        state = merge_script.load_state(state_path)
        merge_script.merge(client, state, state_path, expected)
        passed = merge_script.acceptance_report(client, state, expected) if client.apply else None
    return passed, out.getvalue()


def run_expecting_failure(client, state_path, expected=48):
    with pytest.raises(RuntimeError) as error:
        run(client, state_path, expected)
    return str(error.value)


def count_writes_of_full_run(tmp_path):
    client = FakeClient(make_db(), apply=True)
    run(client, tmp_path / 'count.json')
    return client.writes


def test_dry_run_writes_nothing(tmp_path):
    db = make_db()
    before = copy.deepcopy(db)
    _, out = run(FakeClient(db, apply=False), tmp_path / 'state.json', expected=None)
    assert db == before
    assert not (tmp_path / 'state.json').exists()
    assert '49 biosample(s) link an ExperimentalCondition; 48 link the 4 sources' in out
    assert out.count('[dry run] PATCH /tissues/') == 48


def test_apply_merges_and_rerun_writes_nothing(tmp_path):
    db = make_db()
    state_path = tmp_path / 'state.json'
    passed, out = run(FakeClient(db, apply=True), state_path)
    assert_merged(db)
    assert passed
    assert out.count('PASS') == 5 and 'FAIL' not in out
    rerun = FakeClient(db, apply=True)
    passed, _ = run(rerun, state_path)
    assert passed and rerun.writes == 0
    assert_merged(db)


def test_resume_after_crash_before_each_write(tmp_path):
    for crash_after in range(count_writes_of_full_run(tmp_path)):
        db = make_db()
        state_path = tmp_path / f'crash{crash_after}.json'
        with pytest.raises(Crash):
            run(FakeClient(db, apply=True, crash_after=crash_after), state_path)
        passed, _ = run(FakeClient(db, apply=True), state_path)
        assert passed, crash_after
        assert_merged(db)


def test_resume_after_lost_response_at_each_write(tmp_path):
    for lose_after in range(count_writes_of_full_run(tmp_path)):
        db = make_db()
        state_path = tmp_path / f'lost{lose_after}.json'
        with pytest.raises(Crash):
            run(FakeClient(db, apply=True, lose_response_after=lose_after), state_path)
        passed, _ = run(FakeClient(db, apply=True), state_path)
        assert passed, lose_after
        assert_merged(db)


def test_resume_after_steps_1_and_2(tmp_path):
    # The DB2-75 demo after its first apply stopped at step 3.
    db = make_db()
    state_path = tmp_path / 'state.json'

    def stop_before_step_3(client):
        if client.writes == 1 + len(TISSUES):
            raise Crash()

    with pytest.raises(Crash):
        run(FakeClient(db, apply=True, after_write=stop_before_step_3), state_path)
    assert all(db[source_id]['status'] == 'current' for source_id in SOURCES)
    resumed = FakeClient(db, apply=True)
    passed, out = run(resumed, state_path)
    assert passed and resumed.writes == 5
    assert '0 link the 4 sources, 48 the merged condition' in out
    assert_merged(db)


def test_renamed_alias_held_by_another_type_stops_before_writing(tmp_path):
    db = make_db()
    db['/treatments/holder/'] = {
        '@id': '/treatments/holder/',
        'status': 'deleted',
        'aliases': [f'{merge_script.SOURCE_ALIASES[2]}{merge_script.DELETED_ALIAS_SUFFIX}'],
    }
    before = copy.deepcopy(db)
    client = FakeClient(db, apply=True)
    message = run_expecting_failure(client, tmp_path / 'state.json')
    assert client.writes == 0 and db == before
    assert 'renamed aliases are already taken' in message and '/treatments/holder/' in message


@pytest.mark.parametrize('holder_id, holder', [
    ('/experimental_conditions/holder/', {'lab': '/labs/alex-marson/', 'controlled_terms': TERMS[:1]}),
    ('/treatments/holder/', {}),
])
def test_merged_alias_held_by_another_object_stops_before_writing(tmp_path, holder_id, holder):
    db = make_db()
    db[holder_id] = dict(holder, **{'@id': holder_id, 'status': 'current', 'aliases': [merge_script.MERGED_ALIAS]})
    client = FakeClient(db, apply=True)
    message = run_expecting_failure(client, tmp_path / 'state.json')
    assert client.writes == 0
    assert 'does not match the merged condition' in message


def test_source_with_second_alias_stops_before_writing(tmp_path):
    db = make_db()
    db[SOURCES[1]]['aliases'].append('alex-marson:second_alias')
    client = FakeClient(db, apply=True)
    message = run_expecting_failure(client, tmp_path / 'state.json')
    assert client.writes == 0
    assert 'expected only' in message


def test_source_below_schema_3_stops_before_writing(tmp_path):
    db = make_db()
    db[SOURCES[2]]['schema_version'] = '2'
    client = FakeClient(db, apply=True)
    message = run_expecting_failure(client, tmp_path / 'state.json')
    assert client.writes == 0
    assert 'deploy ExperimentalCondition schema version 3 first' in message


def test_tissue_missing_from_index_stops_before_writing(tmp_path):
    db = make_db()
    before = copy.deepcopy(db)
    client = FakeClient(db, apply=True, hidden={TISSUES[7]})
    message = run_expecting_failure(client, tmp_path / 'state.json')
    assert client.writes == 0 and db == before
    assert '47 biosample(s) link the 4 sources or the merged condition, expected 48' in message


def test_tissue_linked_mid_run_blocks_deletes_until_rerun(tmp_path):
    db = make_db()
    state_path = tmp_path / 'state.json'

    def link_late_tissue(client):
        if client.writes == 1 + len(TISSUES) and '/tissues/late/' not in client.db:
            client.db['/tissues/late/'] = {
                '@id': '/tissues/late/',
                'status': 'current',
                'experimental_conditions': list(SOURCES),
            }

    message = run_expecting_failure(FakeClient(db, apply=True, after_write=link_late_tissue), state_path)
    assert 'still link a source condition, so none was deleted' in message and '/tissues/late/' in message
    assert all(db[source_id]['status'] == 'current' for source_id in SOURCES)
    passed, _ = run(FakeClient(db, apply=True), state_path, expected=49)
    assert passed
    assert db['/tissues/late/']['experimental_conditions'] == [merged_id(db)]


@pytest.mark.parametrize('status', ['current', 'deleted'])
@pytest.mark.parametrize('links', [
    pytest.param([SOURCES[3]], id='one-source-alone'),
    pytest.param(SOURCES[:3], id='three-of-the-four-sources'),
    pytest.param(SOURCES + [OTHER], id='the-four-sources-plus-another'),
    pytest.param([OTHER, OTHER_2], id='two-other-conditions'),
])
def test_unexpected_link_pattern_stops_before_writing(tmp_path, links, status):
    db = make_db()
    db['/tissues/odd/'] = {'@id': '/tissues/odd/', 'status': status, 'experimental_conditions': links}
    before = copy.deepcopy(db)
    client = FakeClient(db, apply=True)
    message = run_expecting_failure(client, tmp_path / 'state.json')
    assert client.writes == 0 and db == before
    assert f'/tissues/odd/ ({status})' in message and 'nothing was written' in message


def test_acceptance_report_flags_multiple_and_deleted_links(tmp_path):
    db = make_db()
    state_path = tmp_path / 'state.json'
    run(FakeClient(db, apply=True), state_path)
    db[TISSUES[5]]['experimental_conditions'].append(OTHER)
    db['/tissues/weissman/']['experimental_conditions'] = [SOURCES[0]]
    out = io.StringIO()
    with redirect_stdout(out):
        passed = merge_script.acceptance_report(FakeClient(db, apply=True), merge_script.load_state(state_path), 48)
    report = out.getvalue()
    assert not passed
    assert 'FAIL: No biosample links more than one' in report and TISSUES[5] in report
    assert 'FAIL: No biosample links a deleted' in report and f'/tissues/weissman/ -> {SOURCES[0]}' in report
