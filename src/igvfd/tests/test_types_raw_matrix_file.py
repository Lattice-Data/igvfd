import pytest


def test_raw_matrix_file_summary_with_aliases(testapp, raw_matrix_file_with_aliases):
    res = testapp.get(raw_matrix_file_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:raw-matrix-file-001'


def test_raw_matrix_file_summary_with_description(testapp, raw_matrix_file_with_description):
    res = testapp.get(raw_matrix_file_with_description['@id'])
    assert res.json.get('summary') == 'Test raw matrix file'
    assert res.json.get('feature_keys') == ['Ensembl gene ID', 'gene symbol']
    assert res.json.get('observation_count') == 9000
    assert res.json.get('feature_counts')[0]['feature_type'] == 'gene'


def test_raw_matrix_file_summary_with_uuid(testapp, raw_matrix_file):
    res = testapp.get(raw_matrix_file['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


def test_raw_matrix_file_required_fields(testapp, other_lab):
    testapp.post_json(
        '/raw_matrix_file',
        {
            'md5sum': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'file_format': 'h5',
            's3_uri': 's3://lattice-test-data/matrix/required-lab.h5',
        },
        status=422
    )
    testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'file_format': 'h5',
            's3_uri': 's3://lattice-test-data/matrix/required-md5sum.h5',
        },
        status=422
    )
    testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            's3_uri': 's3://lattice-test-data/matrix/required-format.h5',
        },
        status=422
    )


def test_raw_matrix_file_file_format_enum(testapp, other_lab):
    testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'file_format': 'h5ad',
            's3_uri': 's3://lattice-test-data/matrix/invalid-format.h5ad',
            'status': 'current',
        },
        status=422
    )


def test_raw_matrix_file_create_success(testapp, other_lab):
    res = testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
            'file_format': 'h5',
            's3_uri': 's3://lattice-test-data/matrix/create-success.h5',
            'status': 'current',
        },
        status=201
    )
    assert res.json['@graph'][0]['file_format'] == 'h5'


def test_raw_matrix_file_create_with_shared_matrix_fields(testapp, other_lab):
    res = testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '0123456789abcdef0123456789abcdef',
            'file_format': 'h5',
            's3_uri': 's3://lattice-test-data/matrix/create-shared-fields.h5',
            'feature_keys': ['Ensembl gene ID', 'gene symbol'],
            'observation_count': 1000,
            'feature_counts': [{'feature_type': 'gene', 'feature_count': 14000}],
            'status': 'current',
        },
        status=201
    )
    assert res.json['@graph'][0]['feature_keys'] == ['Ensembl gene ID', 'gene symbol']
    assert res.json['@graph'][0]['observation_count'] == 1000


def test_raw_matrix_file_rejects_invalid_feature_key(testapp, other_lab):
    testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '89abcdef0123456789abcdef01234567',
            'file_format': 'h5',
            's3_uri': 's3://lattice-test-data/matrix/invalid-feature-key.h5',
            'feature_keys': ['invalid feature key'],
            'status': 'current',
        },
        status=422
    )


def test_raw_matrix_file_rejects_invalid_feature_counts_shape(testapp, other_lab):
    testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'fedcba9876543210fedcba9876543210',
            'file_format': 'h5',
            's3_uri': 's3://lattice-test-data/matrix/invalid-feature-counts.h5',
            'feature_counts': [{'feature_type': 'gene'}],
            'status': 'current',
        },
        status=422
    )


def test_raw_matrix_file_requires_s3_uri_when_file_available(testapp, other_lab):
    testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'cccccccccccccccccccccccccccccccc',
            'file_format': 'h5',
            'no_file_available': False,
            'status': 'current',
        },
        status=422
    )


def test_raw_matrix_file_accepts_no_file_available_without_s3_uri(testapp, other_lab):
    res = testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'dddddddddddddddddddddddddddddddd',
            'file_format': 'h5',
            'no_file_available': True,
            'status': 'current',
        },
        status=201
    )
    assert res.json['@graph'][0]['no_file_available'] is True


def test_raw_matrix_file_rejects_s3_uri_when_no_file_available_true(testapp, other_lab):
    testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
            'file_format': 'h5',
            's3_uri': 's3://lattice-test-data/matrix/conflict.h5',
            'no_file_available': True,
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize(
    'invalid_uri',
    [
        'https://igvfd-test-data/matrix/file.h5',
        '/mnt/data/file.h5',
        'gs://bucket/file.h5',
    ]
)
def test_raw_matrix_file_rejects_invalid_s3_uri_prefix(testapp, other_lab, invalid_uri):
    testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'ffffffffffffffffffffffffffffffff',
            'file_format': 'h5',
            's3_uri': invalid_uri,
            'status': 'current',
        },
        status=422
    )
