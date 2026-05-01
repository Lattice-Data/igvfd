import pytest

SEQUENCE_FILE_READ_COUNT = 15_000_000
CRC64NVME_BASE64_VALID = 'AAAAAAAAAAA'


def _file_post_body(file_type, item):
    """Augment POST bodies for sequence_file read_count and file-available crc64nvme_base64."""
    out = dict(item)
    if (
        file_type == 'sequence_file'
        and 's3_uri' in out
        and out.get('no_file_available') is not True
    ):
        out['read_count'] = SEQUENCE_FILE_READ_COUNT
    if 's3_uri' in out and out.get('no_file_available') is not True:
        out.setdefault('crc64nvme_base64', CRC64NVME_BASE64_VALID)
    return out


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
        _file_post_body(
            file_type,
            {
                'md5sum': '74b87337454200d4d33f80c4663dc5e5',
                'file_format': file_format,
                's3_uri': f's3://lattice-test-data/{s3_path}/required-lab.{file_format}',
            },
        ),
        status=422
    )
    # Missing md5sum
    testapp.post_json(
        endpoint,
        _file_post_body(
            file_type,
            {
                'lab': other_lab['@id'],
                'file_format': file_format,
                's3_uri': f's3://lattice-test-data/{s3_path}/required-md5sum.{file_format}',
            },
        ),
        status=422
    )
    # Missing file_format
    testapp.post_json(
        endpoint,
        _file_post_body(
            file_type,
            {
                'lab': other_lab['@id'],
                'md5sum': '74b87337454200d4d33f80c4663dc5e5',
                's3_uri': f's3://lattice-test-data/{s3_path}/required-format.{file_format}',
            },
        ),
        status=422
    )


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file', 'raw_matrix_file', 'processed_matrix_file'])
def test_file_file_format_enum(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    s3_path = config['s3_path']

    testapp.post_json(
        endpoint,
        _file_post_body(
            file_type,
            {
                'lab': other_lab['@id'],
                'md5sum': '74b87337454200d4d33f80c4663dc5e5',
                'file_format': 'invalid_format',
                's3_uri': f's3://lattice-test-data/{s3_path}/invalid-format.dat',
                'status': 'current',
            },
        ),
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
        _file_post_body(
            file_type,
            {
                'lab': other_lab['@id'],
                'md5sum': 'abc123',
                'file_format': file_format,
                's3_uri': f's3://lattice-test-data/{s3_path}/invalid-md5sum-short.{file_format}',
                'status': 'current',
            },
        ),
        status=422
    )
    # Invalid md5sum pattern (invalid characters)
    testapp.post_json(
        endpoint,
        _file_post_body(
            file_type,
            {
                'lab': other_lab['@id'],
                'md5sum': 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz',
                'file_format': file_format,
                's3_uri': f's3://lattice-test-data/{s3_path}/invalid-md5sum-chars.{file_format}',
                'status': 'current',
            },
        ),
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

    item = _file_post_body(
        file_type,
        {
            'lab': other_lab['@id'],
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            'file_format': file_format,
            's3_uri': f's3://lattice-test-data/{s3_path}/enum-{file_format}.dat',
            'status': 'current',
        },
    )
    res = testapp.post_json(endpoint, item, status=201)
    assert res.json['@graph'][0]['file_format'] == file_format


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file', 'raw_matrix_file', 'processed_matrix_file'])
def test_file_create_success(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    item = _file_post_body(
        file_type,
        {
            'lab': other_lab['@id'],
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            'file_format': file_format,
            's3_uri': f's3://lattice-test-data/{s3_path}/create-success.{file_format}',
            'status': 'current',
        },
    )
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

    item = _file_post_body(
        file_type,
        {
            'lab': other_lab['@id'],
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            'file_format': file_format,
            's3_uri': f's3://lattice-test-data/{s3_path}/all-optional.{file_format}',
            'file_size': 1024000,
            'description': f'Test {file_type.replace("_", " ")} with all fields',
            'status': 'current',
        },
    )
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
        _file_post_body(
            file_type,
            {
                'lab': other_lab['@id'],
                'md5sum': '74b87337454200d4d33f80c4663dc5e5',
                'file_format': file_format,
                's3_uri': f's3://lattice-test-data/{s3_path}/invalid-filesize.{file_format}',
                'file_size': -1,
                'status': 'current',
            },
        ),
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
            'md5sum': '6512bd43d9caa6e02c990b0a82652dca',
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
            'md5sum': 'c20ad4d76fe97759aa27a0c99bff6710',
            'file_format': file_format,
            'no_file_available': True,
            'status': 'current',
        },
        status=201
    )
    assert res.json['@graph'][0]['no_file_available'] is True
    assert 'crc64nvme_base64' not in res.json['@graph'][0]


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file', 'raw_matrix_file', 'processed_matrix_file'])
def test_file_requires_crc64nvme_when_file_available(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    item = {
        'lab': other_lab['@id'],
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': file_format,
        's3_uri': f's3://lattice-test-data/{s3_path}/missing-crc.{file_format}',
        'no_file_available': False,
        'status': 'current',
    }
    if file_type == 'sequence_file':
        item['read_count'] = SEQUENCE_FILE_READ_COUNT
    if config['has_matrix_fields']:
        item['feature_keys'] = ['Ensembl gene ID', 'gene symbol']
        item['observation_count'] = 1000
        item['feature_counts'] = [{'feature_type': 'gene', 'feature_count': 14000}]
    testapp.post_json(endpoint, item, status=422)


@pytest.mark.parametrize(
    'file_type,invalid_crc',
    [
        ('sequence_file', 'AAAAAAAAAA'),
        ('sequence_file', 'AAAAAAAAAAA!'),
        ('sequence_file', 'AAAAAAAAAAAA'),
        ('tabular_file', 'AAAAAAAAAA'),
        ('raw_matrix_file', 'AAAAAAAAAAA==='),
        ('processed_matrix_file', 'not-base64!!'),
    ],
)
def test_file_rejects_invalid_crc64nvme_base64(testapp, other_lab, file_type, invalid_crc):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    item = {
        'lab': other_lab['@id'],
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': file_format,
        's3_uri': f's3://lattice-test-data/{s3_path}/bad-crc.{file_format}',
        'no_file_available': False,
        'crc64nvme_base64': invalid_crc,
        'status': 'current',
    }
    if file_type == 'sequence_file':
        item['read_count'] = SEQUENCE_FILE_READ_COUNT
    if config['has_matrix_fields']:
        item['feature_keys'] = ['Ensembl gene ID', 'gene symbol']
        item['observation_count'] = 1000
        item['feature_counts'] = [{'feature_type': 'gene', 'feature_count': 14000}]
    testapp.post_json(endpoint, item, status=422)


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file', 'raw_matrix_file', 'processed_matrix_file'])
def test_file_rejects_s3_uri_when_no_file_available_true(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    testapp.post_json(
        endpoint,
        _file_post_body(
            file_type,
            {
                'lab': other_lab['@id'],
                'md5sum': 'c51ce410c124a10e0db5e4b97fc2af39',
                'file_format': file_format,
                's3_uri': f's3://lattice-test-data/{s3_path}/conflict.{file_format}',
                'no_file_available': True,
                'status': 'current',
            },
        ),
        status=422
    )


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file'])
def test_file_rejects_non_s3_uri_prefix(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']

    testapp.post_json(
        endpoint,
        _file_post_body(
            file_type,
            {
                'lab': other_lab['@id'],
                'md5sum': 'aab3238922bcc25a6f606eb525ffdc56',
                'file_format': file_format,
                's3_uri': f'https://bucket/path/file.{file_format}',
                'status': 'current',
            },
        ),
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
            'md5sum': 'd3d9446802a44259755d38e6d163e820',
            'file_format': file_format,
            's3_uri': invalid_uri,
            'crc64nvme_base64': CRC64NVME_BASE64_VALID,
            'feature_keys': ['Ensembl gene ID', 'gene symbol'],
            'observation_count': 1000,
            'feature_counts': [{'feature_type': 'gene', 'feature_count': 14000}],
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
            'crc64nvme_base64': CRC64NVME_BASE64_VALID,
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
            'crc64nvme_base64': CRC64NVME_BASE64_VALID,
            'feature_keys': ['invalid feature key'],
            'observation_count': 1000,
            'feature_counts': [{'feature_type': 'gene', 'feature_count': 14000}],
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
            'crc64nvme_base64': CRC64NVME_BASE64_VALID,
            'feature_keys': ['Ensembl gene ID', 'gene symbol'],
            'observation_count': 1000,
            'feature_counts': [{'feature_type': 'gene'}],
            'status': 'current',
        },
        status=422
    )


def test_sequence_file_requires_read_count_when_file_available(testapp, other_lab):
    testapp.post_json(
        '/sequence_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            'file_format': 'fastq',
            's3_uri': 's3://lattice-test-data/sequence/missing-read-count.fastq.gz',
            'crc64nvme_base64': CRC64NVME_BASE64_VALID,
            'status': 'current',
        },
        status=422,
    )


def test_sequence_file_rejects_negative_read_count(testapp, other_lab):
    testapp.post_json(
        '/sequence_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            'file_format': 'fastq',
            's3_uri': 's3://lattice-test-data/sequence/negative-read-count.fastq.gz',
            'crc64nvme_base64': CRC64NVME_BASE64_VALID,
            'read_count': -1,
            'status': 'current',
        },
        status=422,
    )


def test_tabular_file_omits_read_count(testapp, other_lab):
    res = testapp.post_json(
        '/tabular_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            'file_format': 'csv',
            's3_uri': 's3://lattice-test-data/tabular/no-read-count.csv',
            'crc64nvme_base64': CRC64NVME_BASE64_VALID,
            'status': 'current',
        },
        status=201,
    )
    assert 'read_count' not in res.json['@graph'][0]


def test_raw_matrix_file_omits_read_count(testapp, other_lab):
    res = testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '0123456789abcdef0123456789abcdef',
            'file_format': 'h5',
            's3_uri': 's3://lattice-test-data/matrix/no-read-count.h5',
            'crc64nvme_base64': CRC64NVME_BASE64_VALID,
            'feature_keys': ['Ensembl gene ID', 'gene symbol'],
            'observation_count': 1000,
            'feature_counts': [{'feature_type': 'gene', 'feature_count': 14000}],
            'status': 'current',
        },
        status=201,
    )
    assert 'read_count' not in res.json['@graph'][0]


def test_tabular_file_rejects_read_count(testapp, other_lab):
    testapp.post_json(
        '/tabular_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            'file_format': 'csv',
            's3_uri': 's3://lattice-test-data/tabular/read-count-not-allowed.csv',
            'crc64nvme_base64': CRC64NVME_BASE64_VALID,
            'read_count': 100,
            'status': 'current',
        },
        status=422,
    )


def test_sequence_file_reverse_links_include_read_and_index_slots(
    testapp,
    other_lab,
    sequence_file,
    sequence_file_with_aliases,
    sequence_file_with_description,
    droplet_based_library,
):
    read_set = testapp.post_json(
        '/sequence_file_set',
        {
            'lab': other_lab['@id'],
            'library': droplet_based_library['@id'],
            'run_cardinality': 'single-end',
            'read1': sequence_file['@id'],
            'status': 'current',
        },
        status=201,
    ).json['@graph'][0]

    index_set = testapp.post_json(
        '/sequence_file_set',
        {
            'lab': other_lab['@id'],
            'library': droplet_based_library['@id'],
            'run_cardinality': 'paired-end-with-index',
            'read1': sequence_file_with_description['@id'],
            'read2': sequence_file['@id'],
            'index1': sequence_file_with_aliases['@id'],
            'status': 'current',
        },
        status=201,
    ).json['@graph'][0]

    sequence_file_res = testapp.get(sequence_file['@id']).json
    assert read_set['@id'] in sequence_file_res['sequence_file_sets']
    assert index_set['@id'] in sequence_file_res['sequence_file_sets']

    index_file_res = testapp.get(sequence_file_with_aliases['@id']).json
    assert index_set['@id'] in index_file_res['sequence_file_sets']


def test_sequence_file_reverse_links_include_cram_slots(
    testapp,
    other_lab,
    sequence_file_cram,
    droplet_based_library,
):
    cram_set = testapp.post_json(
        '/sequence_file_set',
        {
            'lab': other_lab['@id'],
            'library': droplet_based_library['@id'],
            'run_cardinality': 'single-end',
            'untrimmed_cram': sequence_file_cram['@id'],
            'status': 'current',
        },
        status=201,
    ).json['@graph'][0]

    sequence_file_res = testapp.get(sequence_file_cram['@id']).json
    assert cram_set['@id'] in sequence_file_res['sequence_file_sets']


def test_matrix_files_reverse_links(testapp, matrix_file_set, matrix_file_set_with_processed):
    raw_file = matrix_file_set['raw_matrix_files'][0]
    processed_file = matrix_file_set_with_processed['processed_matrix_files'][0]

    raw_res = testapp.get(raw_file).json
    assert matrix_file_set['@id'] in raw_res['matrix_file_sets']

    processed_res = testapp.get(processed_file).json
    assert matrix_file_set_with_processed['@id'] in processed_res['matrix_file_sets']
