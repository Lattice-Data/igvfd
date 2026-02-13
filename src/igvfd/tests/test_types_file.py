import pytest


# File type configurations
FILE_TYPE_CONFIGS = {
    'sequence_file': {
        'endpoint': '/sequence_file',
        'formats': ['fastq', 'cram'],
        'default_format': 'fastq',
        's3_path': 'sequence',
        'has_matrix_fields': False,
    },
    'tabular_file': {
        'endpoint': '/tabular_file',
        'formats': ['csv', 'tsv'],
        'default_format': 'csv',
        's3_path': 'tabular',
        'has_matrix_fields': False,
    },
    'raw_matrix_file': {
        'endpoint': '/raw_matrix_file',
        'formats': ['h5'],
        'default_format': 'h5',
        's3_path': 'matrix',
        'has_matrix_fields': True,
    },
    'processed_matrix_file': {
        'endpoint': '/processed_matrix_file',
        'formats': ['h5ad'],
        'default_format': 'h5ad',
        's3_path': 'matrix',
        'has_matrix_fields': True,
    },
}


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file', 'raw_matrix_file', 'processed_matrix_file'])
def test_file_summary_with_aliases(testapp, file_type, request):
    config = FILE_TYPE_CONFIGS[file_type]
    fixture = request.getfixturevalue(f'{file_type}_with_aliases')
    res = testapp.get(fixture['@id'])
    assert res.json.get('summary') == f'lattice:{file_type.replace("_", "-")}-001'


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file', 'raw_matrix_file', 'processed_matrix_file'])
def test_file_summary_with_description(testapp, file_type, request):
    config = FILE_TYPE_CONFIGS[file_type]
    fixture = request.getfixturevalue(f'{file_type}_with_description')
    res = testapp.get(fixture['@id'])
    expected_summary = f'Test {file_type.replace("_", " ")}'
    assert res.json.get('summary') == expected_summary


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file', 'raw_matrix_file', 'processed_matrix_file'])
def test_file_summary_with_uuid(testapp, file_type, request):
    config = FILE_TYPE_CONFIGS[file_type]
    fixture = request.getfixturevalue(file_type)
    res = testapp.get(fixture['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file', 'raw_matrix_file', 'processed_matrix_file'])
def test_file_required_fields(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    # Missing lab
    testapp.post_json(
        endpoint,
        {
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            'file_format': file_format,
            's3_uri': f's3://lattice-test-data/{s3_path}/required-lab.{file_format}',
        },
        status=422
    )
    # Missing md5sum
    testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'file_format': file_format,
            's3_uri': f's3://lattice-test-data/{s3_path}/required-md5sum.{file_format}',
        },
        status=422
    )
    # Missing file_format
    testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            's3_uri': f's3://lattice-test-data/{s3_path}/required-format.{file_format}',
        },
        status=422
    )


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file', 'raw_matrix_file', 'processed_matrix_file'])
def test_file_file_format_enum(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    s3_path = config['s3_path']

    testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            'file_format': 'invalid_format',
            's3_uri': f's3://lattice-test-data/{s3_path}/invalid-format.dat',
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file'])
def test_file_md5sum_pattern(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    # Invalid md5sum pattern (too short)
    testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'md5sum': 'abc123',
            'file_format': file_format,
            's3_uri': f's3://lattice-test-data/{s3_path}/invalid-md5sum-short.{file_format}',
            'status': 'current',
        },
        status=422
    )
    # Invalid md5sum pattern (invalid characters)
    testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'md5sum': 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz',
            'file_format': file_format,
            's3_uri': f's3://lattice-test-data/{s3_path}/invalid-md5sum-chars.{file_format}',
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize(
    'file_type,file_format',
    [
        ('sequence_file', 'fastq'),
        ('sequence_file', 'cram'),
        ('tabular_file', 'csv'),
        ('tabular_file', 'tsv'),
    ]
)
def test_file_create_with_file_format_enum_values(testapp, other_lab, file_type, file_format):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    s3_path = config['s3_path']

    item = {
        'lab': other_lab['@id'],
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': file_format,
        's3_uri': f's3://lattice-test-data/{s3_path}/enum-{file_format}.dat',
        'status': 'current',
    }
    res = testapp.post_json(endpoint, item, status=201)
    assert res.json['@graph'][0]['file_format'] == file_format


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file', 'raw_matrix_file', 'processed_matrix_file'])
def test_file_create_success(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    item = {
        'lab': other_lab['@id'],
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': file_format,
        's3_uri': f's3://lattice-test-data/{s3_path}/create-success.{file_format}',
        'status': 'current',
    }
    res = testapp.post_json(endpoint, item, status=201)
    assert res.json['@graph'][0]['lab'] == other_lab['@id']
    assert res.json['@graph'][0]['md5sum'] == '74b87337454200d4d33f80c4663dc5e5'
    assert res.json['@graph'][0]['file_format'] == file_format
    assert res.json['@graph'][0]['s3_uri'] == f's3://lattice-test-data/{s3_path}/create-success.{file_format}'


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file'])
def test_file_create_with_all_optional_fields(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    item = {
        'lab': other_lab['@id'],
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': file_format,
        's3_uri': f's3://lattice-test-data/{s3_path}/all-optional.{file_format}',
        'file_size': 1024000,
        'description': f'Test {file_type.replace("_", " ")} with all fields',
        'status': 'current',
    }
    res = testapp.post_json(endpoint, item, status=201)
    assert res.json['@graph'][0]['file_size'] == 1024000
    assert res.json['@graph'][0]['description'] == f'Test {file_type.replace("_", " ")} with all fields'


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file'])
def test_file_file_size_minimum(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            'file_format': file_format,
            's3_uri': f's3://lattice-test-data/{s3_path}/invalid-filesize.{file_format}',
            'file_size': -1,
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file', 'raw_matrix_file', 'processed_matrix_file'])
def test_file_requires_s3_uri_when_file_available(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']

    testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'md5sum': '11111111111111111111111111111111',
            'file_format': file_format,
            'no_file_available': False,
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file', 'raw_matrix_file', 'processed_matrix_file'])
def test_file_accepts_no_file_available_without_s3_uri(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']

    res = testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'md5sum': '22222222222222222222222222222222',
            'file_format': file_format,
            'no_file_available': True,
            'status': 'current',
        },
        status=201
    )
    assert res.json['@graph'][0]['no_file_available'] is True


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file', 'raw_matrix_file', 'processed_matrix_file'])
def test_file_rejects_s3_uri_when_no_file_available_true(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'md5sum': '33333333333333333333333333333333',
            'file_format': file_format,
            's3_uri': f's3://lattice-test-data/{s3_path}/conflict.{file_format}',
            'no_file_available': True,
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file'])
def test_file_rejects_non_s3_uri_prefix(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']

    testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'md5sum': '44444444444444444444444444444444',
            'file_format': file_format,
            's3_uri': f'https://bucket/path/file.{file_format}',
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize(
    'file_type,invalid_uri',
    [
        ('raw_matrix_file', 'https://igvfd-test-data/matrix/file.h5'),
        ('raw_matrix_file', '/mnt/data/file.h5'),
        ('raw_matrix_file', 'gs://bucket/file.h5'),
        ('processed_matrix_file', 'https://igvfd-test-data/matrix/file.h5ad'),
        ('processed_matrix_file', '/mnt/data/file.h5ad'),
        ('processed_matrix_file', 'gs://bucket/file.h5ad'),
    ]
)
def test_file_rejects_invalid_s3_uri_prefix(testapp, other_lab, file_type, invalid_uri):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']

    testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'md5sum': 'ffffffffffffffffffffffffffffffff',
            'file_format': file_format,
            's3_uri': invalid_uri,
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize('file_type', ['raw_matrix_file', 'processed_matrix_file'])
def test_matrix_file_create_with_shared_matrix_fields(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    res = testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'md5sum': '0123456789abcdef0123456789abcdef',
            'file_format': file_format,
            's3_uri': f's3://lattice-test-data/{s3_path}/create-shared-fields.{file_format}',
            'feature_keys': ['Ensembl gene ID', 'gene symbol'],
            'observation_count': 1000,
            'feature_counts': [{'feature_type': 'gene', 'feature_count': 14000}],
            'status': 'current',
        },
        status=201
    )
    assert res.json['@graph'][0]['feature_keys'] == ['Ensembl gene ID', 'gene symbol']
    assert res.json['@graph'][0]['observation_count'] == 1000


@pytest.mark.parametrize('file_type', ['raw_matrix_file', 'processed_matrix_file'])
def test_matrix_file_rejects_invalid_feature_key(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'md5sum': '89abcdef0123456789abcdef01234567',
            'file_format': file_format,
            's3_uri': f's3://lattice-test-data/{s3_path}/invalid-feature-key.{file_format}',
            'feature_keys': ['invalid feature key'],
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize('file_type', ['raw_matrix_file', 'processed_matrix_file'])
def test_matrix_file_rejects_invalid_feature_counts_shape(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'md5sum': 'fedcba9876543210fedcba9876543210',
            'file_format': file_format,
            's3_uri': f's3://lattice-test-data/{s3_path}/invalid-feature-counts.{file_format}',
            'feature_counts': [{'feature_type': 'gene'}],
            'status': 'current',
        },
        status=422
    )
