import pytest

from igvfd.audit.formatter import path_to_text
from igvfd.audit.matrix_file import (
    audit_matrix_file_derived_from_incomplete_sequence_file_set,
    audit_matrix_file_missing_md5sum,
    audit_raw_matrix_file_software_without_version,
)

MD5SUM_VALID = '74b87337454200d4d33f80c4663dc5e5'


def _audit_errors(res):
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    return errors_list


def test_software_without_version_audit():
    value = {
        '@type': ['RawMatrixFile'],
        '@id': '/raw-matrix-files/IGVFDTEST0001/',
        'software': 'Cell Ranger',
    }
    failures = list(audit_raw_matrix_file_software_without_version(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'missing software version'


def test_software_with_version_no_audit():
    value = {
        '@type': ['RawMatrixFile'],
        '@id': '/raw-matrix-files/IGVFDTEST0001/',
        'software': 'Cell Ranger',
        'software_version': '7.1.0',
    }
    failures = list(audit_raw_matrix_file_software_without_version(value, {}))
    assert len(failures) == 0


def test_no_software_no_audit():
    value = {
        '@type': ['RawMatrixFile'],
        '@id': '/raw-matrix-files/IGVFDTEST0001/',
    }
    failures = list(audit_raw_matrix_file_software_without_version(value, {}))
    assert len(failures) == 0


def test_raw_matrix_file_fixture_clean(indexer_testapp, raw_matrix_file):
    res = indexer_testapp.get(raw_matrix_file['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert not any(
        error['category'] == 'missing software version'
        for error in errors_list
    )


def test_raw_matrix_file_software_without_version_audit(
    testapp,
    indexer_testapp,
    raw_matrix_file_without_software_version,
):
    res = indexer_testapp.get(
        raw_matrix_file_without_software_version['@id'] + '@@index-data'
    )
    errors_list = _audit_errors(res)
    assert any(
        error['category'] == 'missing software version'
        for error in errors_list
    )


def test_raw_matrix_file_audit_clears_after_adding_version(
    testapp,
    indexer_testapp,
    raw_matrix_file_without_software_version,
):
    testapp.patch_json(
        raw_matrix_file_without_software_version['@id'],
        {'software_version': '7.2.0'},
        status=200,
    )
    res = indexer_testapp.get(
        raw_matrix_file_without_software_version['@id'] + '@@index-data'
    )
    errors_list = _audit_errors(res)
    assert not any(
        error['category'] == 'missing software version'
        for error in errors_list
    )


@pytest.mark.parametrize(
    'object_type,obj_id',
    [
        ('RawMatrixFile', '/raw-matrix-files/IGVFDTEST0001/'),
        ('ProcessedMatrixFile', '/processed-matrix-files/IGVFDTEST0001/'),
    ],
)
def test_missing_md5sum_audit(object_type, obj_id):
    value = {
        '@type': [object_type],
        '@id': obj_id,
        's3_uri': 's3://lattice-test-data/matrix/file.h5',
    }
    failures = list(audit_matrix_file_missing_md5sum(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'missing md5sum'
    assert failures[0].__json__()['level_name'] == 'ERROR'
    assert 'GEO' in failures[0].detail


def test_missing_md5sum_no_audit_with_md5sum():
    value = {
        '@type': ['RawMatrixFile'],
        '@id': '/raw-matrix-files/IGVFDTEST0001/',
        's3_uri': 's3://lattice-test-data/matrix/file.h5',
        'md5sum': MD5SUM_VALID,
    }
    failures = list(audit_matrix_file_missing_md5sum(value, {}))
    assert len(failures) == 0


def test_missing_md5sum_no_audit_without_file():
    value = {
        '@type': ['ProcessedMatrixFile'],
        '@id': '/processed-matrix-files/IGVFDTEST0001/',
        'no_file_available': True,
    }
    failures = list(audit_matrix_file_missing_md5sum(value, {}))
    assert len(failures) == 0


@pytest.mark.parametrize('fixture_name', ['raw_matrix_file', 'processed_matrix_file'])
def test_matrix_file_missing_md5sum_audit_integration(
    testapp,
    indexer_testapp,
    fixture_name,
    request,
):
    matrix_file = request.getfixturevalue(fixture_name)
    res = indexer_testapp.get(matrix_file['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing md5sum'
        for error in res.json['audit'].get('ERROR', [])
    )


@pytest.mark.parametrize('fixture_name', ['raw_matrix_file', 'processed_matrix_file'])
def test_matrix_file_md5sum_audit_clears_after_adding_md5sum(
    testapp,
    indexer_testapp,
    fixture_name,
    request,
):
    matrix_file = request.getfixturevalue(fixture_name)
    testapp.patch_json(matrix_file['@id'], {'md5sum': MD5SUM_VALID}, status=200)
    res = indexer_testapp.get(matrix_file['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert not any(
        error['category'] == 'missing md5sum'
        for error in errors_list
    )


def test_sequence_file_no_md5sum_audit(indexer_testapp, sequence_file):
    res = indexer_testapp.get(sequence_file['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert not any(
        error['category'] == 'missing md5sum'
        for error in errors_list
    )


INCOMPLETE_DERIVED_FROM = 'incomplete derived from'
SET_ID = '/sequence-file-sets/b2a1f0d2-0000-4000-8000-000000000001/'
R1 = '/sequence-files/IGVFDTEST0R1/'
R2 = '/sequence-files/IGVFDTEST0R2/'
I1 = '/sequence-files/IGVFDTEST0I1/'
I2 = '/sequence-files/IGVFDTEST0I2/'


class _StubRequest:
    def __init__(self, objects):
        self.objects = objects

    def embed(self, path, *args):
        return self.objects[path.split('@@')[0]]


def _stub_system(set_status='current', in_set=(R1, R2, I1, I2)):
    slots = dict(zip(('read1', 'read2', 'index1', 'index2'), in_set))
    objects = {
        SET_ID: {'@id': SET_ID, 'status': set_status, **slots},
        '/raw-matrix-files/IGVFDTEST0001/': {},
    }
    for file_id in in_set:
        objects[file_id] = {'@id': file_id, 'sequence_file_sets': [SET_ID]}
    return {'request': _StubRequest(objects)}


def _matrix_value(derived_from):
    value = {
        '@type': ['RawMatrixFile'],
        '@id': '/raw-matrix-files/IGVFDTEST0001/',
    }
    if derived_from is not None:
        value['derived_from'] = derived_from
    return value


def test_derived_from_complete_set_no_audit():
    failures = list(audit_matrix_file_derived_from_incomplete_sequence_file_set(
        _matrix_value([R1, R2, I1, I2]), _stub_system()))
    assert failures == []


def test_derived_from_missing_index_reads_audit():
    failures = list(audit_matrix_file_derived_from_incomplete_sequence_file_set(
        _matrix_value([R1, R2]), _stub_system()))
    assert len(failures) == 1
    assert failures[0].category == INCOMPLETE_DERIVED_FROM
    assert failures[0].__json__()['level_name'] == 'ERROR'
    assert 'IGVFDTEST0I1' in failures[0].detail
    assert 'IGVFDTEST0I2' in failures[0].detail
    assert 'IGVFDTEST0R1' not in failures[0].detail.split('missing')[1]


def test_derived_from_absent_no_audit():
    failures = list(audit_matrix_file_derived_from_incomplete_sequence_file_set(
        _matrix_value(None), _stub_system()))
    assert failures == []


def test_derived_from_deleted_set_no_audit():
    failures = list(audit_matrix_file_derived_from_incomplete_sequence_file_set(
        _matrix_value([R1]), _stub_system(set_status='deleted')))
    assert failures == []


def test_derived_from_file_outside_any_set_no_audit():
    system = _stub_system()
    other = '/raw-matrix-files/IGVFDTEST0002/'
    system['request'].objects[other] = {'@id': other}
    failures = list(audit_matrix_file_derived_from_incomplete_sequence_file_set(
        _matrix_value([other]), system))
    assert failures == []


def _incomplete_errors(res):
    return [
        error for error in _audit_errors(res)
        if error['category'] == INCOMPLETE_DERIVED_FROM
    ]


@pytest.mark.parametrize('fixture_name', ['raw_matrix_file', 'processed_matrix_file'])
def test_matrix_file_derived_from_partial_set_audit(
    testapp,
    indexer_testapp,
    fixture_name,
    request,
    sequence_file_set_illumina_paired_end,
    sequence_file,
    sequence_file_with_description,
):
    matrix_file = request.getfixturevalue(fixture_name)
    testapp.patch_json(
        matrix_file['@id'],
        {'derived_from': [sequence_file['@id']]},
        status=200,
    )
    res = indexer_testapp.get(matrix_file['@id'] + '@@index-data')
    errors = _incomplete_errors(res)
    assert len(errors) == 1
    assert errors[0]['level_name'] == 'ERROR'
    assert path_to_text(sequence_file_with_description['@id']) in errors[0]['detail']


@pytest.mark.parametrize('fixture_name', ['raw_matrix_file', 'processed_matrix_file'])
def test_matrix_file_derived_from_full_set_no_audit(
    testapp,
    indexer_testapp,
    fixture_name,
    request,
    sequence_file_set_illumina_paired_end,
    sequence_file,
    sequence_file_with_description,
):
    matrix_file = request.getfixturevalue(fixture_name)
    testapp.patch_json(
        matrix_file['@id'],
        {'derived_from': [sequence_file['@id'], sequence_file_with_description['@id']]},
        status=200,
    )
    res = indexer_testapp.get(matrix_file['@id'] + '@@index-data')
    assert _incomplete_errors(res) == []


def test_matrix_file_derived_from_audit_fires_on_added_index_read(
    testapp,
    indexer_testapp,
    raw_matrix_file,
    sequence_file_set_illumina_paired_end,
    sequence_file,
    sequence_file_with_description,
    sequence_file_with_aliases,
):
    testapp.patch_json(
        raw_matrix_file['@id'],
        {'derived_from': [sequence_file['@id'], sequence_file_with_description['@id']]},
        status=200,
    )
    testapp.patch_json(
        sequence_file_set_illumina_paired_end['@id'],
        {
            'index1': sequence_file_with_aliases['@id'],
            'run_cardinality': 'paired-end-with-index',
        },
        status=200,
    )
    res = indexer_testapp.get(raw_matrix_file['@id'] + '@@index-data')
    errors = _incomplete_errors(res)
    assert len(errors) == 1
    assert path_to_text(sequence_file_with_aliases['@id']) in errors[0]['detail']
