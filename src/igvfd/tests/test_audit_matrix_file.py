import pytest

from igvfd.audit.matrix_file import (
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
