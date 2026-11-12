import pytest

from igvfd.audit.file import audit_file_missing_file_set


CATEGORY = 'missing file set'


class _Request:
    '''Answers the status lookups the audit makes for each linked file set.'''

    def __init__(self, statuses):
        self.statuses = statuses

    def embed(self, path, view):
        return {'status': self.statuses[path]}


def _audit_errors(res):
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    return errors_list


def _missing_file_set_errors(indexer_testapp, item):
    res = indexer_testapp.get(item['@id'] + '@@index-data')
    return [
        error for error in _audit_errors(res)
        if error['category'] == CATEGORY
    ]


def _failures(value, statuses=None):
    return list(audit_file_missing_file_set(value, {'request': _Request(statuses or {})}))


SEQUENCE_FILE = {
    '@type': ['SequenceFile', 'File', 'Item'],
    '@id': '/sequence-files/IGVFDTEST0001/',
    'status': 'current',
}
RAW_MATRIX_FILE = {
    '@type': ['RawMatrixFile', 'File', 'Item'],
    '@id': '/raw-matrix-files/IGVFDTEST0002/',
    'status': 'current',
}
SET_A = '/sequence-file-sets/IGVFDTESTSETA/'
SET_B = '/sequence-file-sets/IGVFDTESTSETB/'
MATRIX_SET = '/matrix-file-sets/IGVFDTESTSETM/'


def test_file_without_file_set_audit():
    failures = _failures({**SEQUENCE_FILE, 'sequence_file_sets': []})
    assert len(failures) == 1
    assert failures[0].category == CATEGORY
    assert failures[0].level == 60
    assert failures[0].detail.startswith(
        'Sequence file [IGVFDTEST0001](/sequence-files/IGVFDTEST0001/) '
        'is not linked from any file set.'
    )


def test_file_without_reverse_link_property_audit():
    failures = _failures(dict(SEQUENCE_FILE))
    assert [failure.category for failure in failures] == [CATEGORY]


def test_file_in_current_file_set_no_audit():
    value = {**SEQUENCE_FILE, 'sequence_file_sets': [SET_A]}
    assert _failures(value, {SET_A: 'current'}) == []


def test_matrix_file_in_current_file_set_no_audit():
    value = {**RAW_MATRIX_FILE, 'matrix_file_sets': [MATRIX_SET]}
    assert _failures(value, {MATRIX_SET: 'current'}) == []


def test_deleted_file_without_file_set_no_audit():
    value = {**SEQUENCE_FILE, 'status': 'deleted', 'sequence_file_sets': []}
    assert _failures(value) == []


def test_file_in_one_deleted_file_set_audit():
    value = {**SEQUENCE_FILE, 'sequence_file_sets': [SET_A]}
    failures = _failures(value, {SET_A: 'deleted'})
    assert len(failures) == 1
    assert (
        'is linked only from deleted file set '
        '[IGVFDTESTSETA](/sequence-file-sets/IGVFDTESTSETA/).'
    ) in failures[0].detail


def test_file_in_two_deleted_file_sets_audit():
    value = {**SEQUENCE_FILE, 'sequence_file_sets': [SET_A, SET_B]}
    failures = _failures(value, {SET_A: 'deleted', SET_B: 'deleted'})
    assert len(failures) == 1
    assert (
        'is linked only from deleted file sets '
        '[IGVFDTESTSETA](/sequence-file-sets/IGVFDTESTSETA/), '
        '[IGVFDTESTSETB](/sequence-file-sets/IGVFDTESTSETB/).'
    ) in failures[0].detail


def test_file_in_deleted_and_current_file_sets_no_audit():
    value = {**SEQUENCE_FILE, 'sequence_file_sets': [SET_A, SET_B]}
    assert _failures(value, {SET_A: 'deleted', SET_B: 'current'}) == []


def test_matrix_file_in_deleted_file_set_audit():
    value = {**RAW_MATRIX_FILE, 'matrix_file_sets': [MATRIX_SET]}
    failures = _failures(value, {MATRIX_SET: 'deleted'})
    assert len(failures) == 1
    assert failures[0].detail.startswith(
        'Raw matrix file [IGVFDTEST0002](/raw-matrix-files/IGVFDTEST0002/) '
        'is linked only from deleted file set '
    )


@pytest.mark.parametrize('file_fixture', [
    'sequence_file',
    'raw_matrix_file',
    'processed_matrix_file',
])
def test_file_without_file_set_index_data_audit(request, indexer_testapp, file_fixture):
    item = request.getfixturevalue(file_fixture)
    errors = _missing_file_set_errors(indexer_testapp, item)
    assert len(errors) == 1
    assert errors[0]['level_name'] == 'ERROR'
    assert 'is not linked from any file set' in errors[0]['detail']


@pytest.mark.parametrize('file_fixture,set_fixture', [
    ('sequence_file', 'sequence_file_set_illumina_single_end'),
    ('raw_matrix_file', 'matrix_file_set'),
    ('processed_matrix_file', 'matrix_file_set_with_processed'),
])
def test_file_in_file_set_index_data_no_audit(request, indexer_testapp, file_fixture, set_fixture):
    item = request.getfixturevalue(file_fixture)
    request.getfixturevalue(set_fixture)
    assert _missing_file_set_errors(indexer_testapp, item) == []


@pytest.mark.parametrize('file_fixture,set_fixture', [
    ('sequence_file', 'sequence_file_set_illumina_single_end'),
    ('raw_matrix_file', 'matrix_file_set'),
    ('processed_matrix_file', 'matrix_file_set_with_processed'),
])
def test_file_set_deleted_index_data_audit(request, testapp, indexer_testapp, file_fixture, set_fixture):
    item = request.getfixturevalue(file_fixture)
    file_set = request.getfixturevalue(set_fixture)
    testapp.patch_json(file_set['@id'], {'status': 'deleted'}, status=200)
    errors = _missing_file_set_errors(indexer_testapp, item)
    assert len(errors) == 1
    assert 'is linked only from deleted file set' in errors[0]['detail']
    assert file_set['@id'] in errors[0]['detail']


@pytest.mark.parametrize('file_fixture', [
    'sequence_file',
    'raw_matrix_file',
    'processed_matrix_file',
])
def test_deleted_file_without_file_set_index_data_no_audit(request, testapp, indexer_testapp, file_fixture):
    item = request.getfixturevalue(file_fixture)
    testapp.patch_json(item['@id'], {'status': 'deleted'}, status=200)
    assert _missing_file_set_errors(indexer_testapp, item) == []


def test_tabular_file_without_file_set_no_audit(indexer_testapp, tabular_file):
    assert _missing_file_set_errors(indexer_testapp, tabular_file) == []
