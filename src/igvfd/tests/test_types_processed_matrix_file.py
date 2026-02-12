import pytest


def test_processed_matrix_file_summary_with_aliases(testapp, processed_matrix_file_with_aliases):
    res = testapp.get(processed_matrix_file_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:processed-matrix-file-001'


def test_processed_matrix_file_summary_with_description(testapp, processed_matrix_file_with_description):
    res = testapp.get(processed_matrix_file_with_description['@id'])
    assert res.json.get('summary') == 'Test processed matrix file'


def test_processed_matrix_file_summary_with_uuid(testapp, processed_matrix_file):
    res = testapp.get(processed_matrix_file['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


def test_processed_matrix_file_required_fields(testapp, other_lab):
    testapp.post_json(
        '/processed_matrix_file',
        {
            'md5sum': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'file_format': 'h5ad',
            's3_uri': 's3://lattice-test-data/matrix/required-lab.h5ad',
        },
        status=422
    )
    testapp.post_json(
        '/processed_matrix_file',
        {
            'lab': other_lab['@id'],
            'file_format': 'h5ad',
            's3_uri': 's3://lattice-test-data/matrix/required-md5sum.h5ad',
        },
        status=422
    )
    testapp.post_json(
        '/processed_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            's3_uri': 's3://lattice-test-data/matrix/required-format.h5ad',
        },
        status=422
    )


def test_processed_matrix_file_file_format_enum(testapp, other_lab):
    testapp.post_json(
        '/processed_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'file_format': 'h5',
            's3_uri': 's3://lattice-test-data/matrix/invalid-format.h5',
            'status': 'current',
        },
        status=422
    )


def test_processed_matrix_file_create_success(testapp, other_lab):
    res = testapp.post_json(
        '/processed_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
            'file_format': 'h5ad',
            's3_uri': 's3://lattice-test-data/matrix/create-success.h5ad',
            'status': 'current',
        },
        status=201
    )
    assert res.json['@graph'][0]['file_format'] == 'h5ad'


def test_processed_matrix_file_requires_s3_uri_when_file_available(testapp, other_lab):
    testapp.post_json(
        '/processed_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'cccccccccccccccccccccccccccccccc',
            'file_format': 'h5ad',
            'status': 'current',
        },
        status=422
    )


def test_processed_matrix_file_accepts_no_file_available_without_s3_uri(testapp, other_lab):
    res = testapp.post_json(
        '/processed_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'dddddddddddddddddddddddddddddddd',
            'file_format': 'h5ad',
            'no_file_available': True,
            'status': 'current',
        },
        status=201
    )
    assert res.json['@graph'][0]['no_file_available'] is True


def test_processed_matrix_file_rejects_s3_uri_when_no_file_available_true(testapp, other_lab):
    testapp.post_json(
        '/processed_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
            'file_format': 'h5ad',
            's3_uri': 's3://lattice-test-data/matrix/conflict.h5ad',
            'no_file_available': True,
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize(
    'invalid_uri',
    [
        'https://igvfd-test-data/matrix/file.h5ad',
        '/mnt/data/file.h5ad',
        'gs://bucket/file.h5ad',
    ]
)
def test_processed_matrix_file_rejects_invalid_s3_uri_prefix(testapp, other_lab, invalid_uri):
    testapp.post_json(
        '/processed_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'ffffffffffffffffffffffffffffffff',
            'file_format': 'h5ad',
            's3_uri': invalid_uri,
            'status': 'current',
        },
        status=422
    )
