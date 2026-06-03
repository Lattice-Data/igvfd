from igvfd.audit.matrix_file import (
    audit_raw_matrix_file_software_without_version,
)


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
