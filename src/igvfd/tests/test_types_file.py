import pytest

SEQUENCE_FILE_READ_COUNT = 15_000_000
CRC64NVME_BASE64_VALID = 'AAAAAAAAAAA'
RAW_MATRIX_FILE_METADATA = {
    'software': 'Cell Ranger',
    'software_version': '7.1.0',
    'genome_assembly': 'GRCh38',
    'is_multiplexed': False,
}

PROCESSED_MATRIX_FILE_METADATA = {
    'is_multiplexed': False,
}


def _file_post_body(file_type, item):
    """Augment POST bodies for sequence_file read_count and file-available crc64nvme_base64."""
    out = dict(item)
    if file_type == 'raw_matrix_file':
        for key, value in RAW_MATRIX_FILE_METADATA.items():
            out.setdefault(key, value)
    if file_type == 'processed_matrix_file':
        for key, value in PROCESSED_MATRIX_FILE_METADATA.items():
            out.setdefault(key, value)
    if (
        file_type == 'sequence_file'
        and 's3_uri' in out
        and out.get('no_file_available') is not True
    ):
        out['read_count'] = SEQUENCE_FILE_READ_COUNT
    if 's3_uri' in out and out.get('no_file_available') is not True:
        out.setdefault('crc64nvme_base64', CRC64NVME_BASE64_VALID)
    return out


def _augment_matrix_file_post(file_type, item):
    """Add matrix file required metadata when building matrix file POST bodies."""
    out = dict(item)
    if file_type == 'raw_matrix_file':
        out.update(RAW_MATRIX_FILE_METADATA)
    if file_type == 'processed_matrix_file':
        for key, value in PROCESSED_MATRIX_FILE_METADATA.items():
            out.setdefault(key, value)
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
        'formats': ['h5', 'h5ad'],
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
    fixture = request.getfixturevalue(f'{file_type}_with_aliases')
    res = testapp.get(fixture['@id'])
    alias_summaries = {
        'raw_matrix_file': 'lattice:pytest-raw-matrix-file-001',
        'processed_matrix_file': 'lattice:pytest-processed-matrix-file-001',
    }
    expected = alias_summaries.get(
        file_type,
        f'lattice:{file_type.replace("_", "-")}-001',
    )
    assert res.json.get('summary') == expected


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
                'file_format': file_format,
                's3_uri': f's3://lattice-test-data/{s3_path}/required-lab.{file_format}',
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
                'file_format': 'invalid_format',
                's3_uri': f's3://lattice-test-data/{s3_path}/invalid-format.dat',
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
            'file_format': file_format,
            's3_uri': f's3://lattice-test-data/{s3_path}/create-success.{file_format}',
            'status': 'current',
        },
    )
    res = testapp.post_json(endpoint, item, status=201)
    assert res.json['@graph'][0]['lab'] == other_lab['@id']
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
        _augment_matrix_file_post(
            file_type,
            {
                'lab': other_lab['@id'],
                'file_format': file_format,
                'no_file_available': False,
                'status': 'current',
            },
        ),
        status=422
    )


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file', 'raw_matrix_file', 'processed_matrix_file'])
def test_file_accepts_no_file_available_without_s3_uri(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']

    res = testapp.post_json(
        endpoint,
        _augment_matrix_file_post(
            file_type,
            {
                'lab': other_lab['@id'],
                'file_format': file_format,
                'no_file_available': True,
                'status': 'current',
            },
        ),
        status=201
    )
    assert res.json['@graph'][0]['no_file_available'] is True
    assert 'crc64nvme_base64' not in res.json['@graph'][0]


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file', 'raw_matrix_file', 'processed_matrix_file'])
@pytest.mark.parametrize('no_file_available', [None, False, True])
def test_file_create_success_no_file_available_modes(testapp, other_lab, file_type, no_file_available):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    item = _augment_matrix_file_post(
        file_type,
        {
            'lab': other_lab['@id'],
            'file_format': file_format,
            'status': 'current',
        },
    )

    if no_file_available is True:
        item['no_file_available'] = True
    else:
        item['s3_uri'] = (
            f's3://lattice-test-data/{s3_path}/create-mode-'
            f'{str(no_file_available).lower()}.{file_format}'
        )
        item['crc64nvme_base64'] = CRC64NVME_BASE64_VALID
        if no_file_available is False:
            item['no_file_available'] = False
        if file_type == 'sequence_file':
            item['read_count'] = SEQUENCE_FILE_READ_COUNT
        if config['has_matrix_fields']:
            item['feature_keys'] = ['Ensembl gene ID', 'gene symbol']
            item['observation_count'] = 1000
            item['feature_counts'] = [{'feature_type': 'gene', 'feature_count': 14000}]

    res = testapp.post_json(endpoint, item, status=201)
    posted = res.json['@graph'][0]
    if no_file_available is True:
        assert posted['no_file_available'] is True
        assert 's3_uri' not in posted
        assert 'crc64nvme_base64' not in posted
    else:
        assert posted['s3_uri'] == item['s3_uri']
        assert posted['crc64nvme_base64'] == CRC64NVME_BASE64_VALID


@pytest.mark.parametrize('file_type', ['sequence_file', 'tabular_file', 'raw_matrix_file', 'processed_matrix_file'])
def test_file_requires_crc64nvme_when_file_available(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    item = _augment_matrix_file_post(
        file_type,
        {
            'lab': other_lab['@id'],
            'file_format': file_format,
            's3_uri': f's3://lattice-test-data/{s3_path}/missing-crc.{file_format}',
            'no_file_available': False,
            'status': 'current',
        },
    )
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

    item = _augment_matrix_file_post(
        file_type,
        {
            'lab': other_lab['@id'],
            'file_format': file_format,
            's3_uri': f's3://lattice-test-data/{s3_path}/bad-crc.{file_format}',
            'no_file_available': False,
            'crc64nvme_base64': invalid_crc,
            'status': 'current',
        },
    )
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
        _augment_matrix_file_post(
            file_type,
            {
                'lab': other_lab['@id'],
                'file_format': file_format,
                's3_uri': invalid_uri,
                'crc64nvme_base64': CRC64NVME_BASE64_VALID,
                'feature_keys': ['Ensembl gene ID', 'gene symbol'],
                'observation_count': 1000,
                'feature_counts': [{'feature_type': 'gene', 'feature_count': 14000}],
                'status': 'current',
            },
        ),
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
        _augment_matrix_file_post(
            file_type,
            {
                'lab': other_lab['@id'],
                'file_format': file_format,
                's3_uri': f's3://lattice-test-data/{s3_path}/create-shared-fields.{file_format}',
                'crc64nvme_base64': CRC64NVME_BASE64_VALID,
                'feature_keys': ['Ensembl gene ID', 'gene symbol'],
                'observation_count': 1000,
                'feature_counts': [{'feature_type': 'gene', 'feature_count': 14000}],
                'status': 'current',
            },
        ),
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
        _augment_matrix_file_post(
            file_type,
            {
                'lab': other_lab['@id'],
                'file_format': file_format,
                's3_uri': f's3://lattice-test-data/{s3_path}/invalid-feature-key.{file_format}',
                'crc64nvme_base64': CRC64NVME_BASE64_VALID,
                'feature_keys': ['invalid feature key'],
                'observation_count': 1000,
                'feature_counts': [{'feature_type': 'gene', 'feature_count': 14000}],
                'status': 'current',
            },
        ),
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
        _augment_matrix_file_post(
            file_type,
            {
                'lab': other_lab['@id'],
                'file_format': file_format,
                's3_uri': f's3://lattice-test-data/{s3_path}/invalid-feature-counts.{file_format}',
                'crc64nvme_base64': CRC64NVME_BASE64_VALID,
                'feature_keys': ['Ensembl gene ID', 'gene symbol'],
                'observation_count': 1000,
                'feature_counts': [{'feature_type': 'gene'}],
                'status': 'current',
            },
        ),
        status=422
    )


def test_sequence_file_requires_read_count_when_file_available(testapp, other_lab):
    testapp.post_json(
        '/sequence_file',
        {
            'lab': other_lab['@id'],
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
        _augment_matrix_file_post(
            'raw_matrix_file',
            {
                'lab': other_lab['@id'],
                'file_format': 'h5',
                's3_uri': 's3://lattice-test-data/matrix/no-read-count.h5',
                'crc64nvme_base64': CRC64NVME_BASE64_VALID,
                'feature_keys': ['Ensembl gene ID', 'gene symbol'],
                'observation_count': 1000,
                'feature_counts': [{'feature_type': 'gene', 'feature_count': 14000}],
                'status': 'current',
            },
        ),
        status=201,
    )
    assert 'read_count' not in res.json['@graph'][0]


def test_tabular_file_rejects_read_count(testapp, other_lab):
    testapp.post_json(
        '/tabular_file',
        {
            'lab': other_lab['@id'],
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


def test_raw_matrix_file_accepts_new_feature_keys(testapp, other_lab):
    res = testapp.post_json(
        '/raw_matrix_file',
        _augment_matrix_file_post(
            'raw_matrix_file',
            {
                'lab': other_lab['@id'],
                'file_format': 'h5',
                's3_uri': 's3://lattice-test-data/matrix/new-feature-keys.h5',
                'crc64nvme_base64': CRC64NVME_BASE64_VALID,
                'feature_keys': ['crispr guide ID', 'hash oligo'],
                'observation_count': 500,
                'feature_counts': [{'feature_type': 'gene', 'feature_count': 1000}],
                'status': 'current',
            },
        ),
        status=201,
    )
    assert set(res.json['@graph'][0]['feature_keys']) == {'crispr guide ID', 'hash oligo'}


def test_processed_matrix_file_rejects_raw_only_feature_keys(testapp, other_lab):
    testapp.post_json(
        '/processed_matrix_file',
        {
            'lab': other_lab['@id'],
            'file_format': 'h5ad',
            's3_uri': 's3://lattice-test-data/matrix/reject-raw-feature-key.h5ad',
            'crc64nvme_base64': CRC64NVME_BASE64_VALID,
            'feature_keys': ['crispr guide ID'],
            'observation_count': 500,
            'feature_counts': [{'feature_type': 'gene', 'feature_count': 1000}],
            'is_multiplexed': False,
            'status': 'current',
        },
        status=422,
    )


@pytest.mark.parametrize('file_type', ['raw_matrix_file', 'processed_matrix_file'])
def test_matrix_file_accepts_guide_capture_feature_type(testapp, other_lab, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    res = testapp.post_json(
        endpoint,
        _augment_matrix_file_post(
            file_type,
            {
                'lab': other_lab['@id'],
                'file_format': file_format,
                's3_uri': f's3://lattice-test-data/{s3_path}/guide-capture.{file_format}',
                'crc64nvme_base64': CRC64NVME_BASE64_VALID,
                'feature_keys': ['Ensembl gene ID'],
                'observation_count': 800,
                'feature_counts': [{'feature_type': 'guide capture', 'feature_count': 2000}],
                'status': 'current',
            },
        ),
        status=201,
    )
    assert res.json['@graph'][0]['feature_counts'][0]['feature_type'] == 'guide capture'


@pytest.mark.parametrize('file_type', ['raw_matrix_file', 'processed_matrix_file'])
def test_matrix_file_create_with_samples(testapp, other_lab, tissue, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    res = testapp.post_json(
        endpoint,
        _augment_matrix_file_post(
            file_type,
            {
                'lab': other_lab['@id'],
                'file_format': file_format,
                's3_uri': f's3://lattice-test-data/{s3_path}/with-samples.{file_format}',
                'crc64nvme_base64': CRC64NVME_BASE64_VALID,
                'samples': [tissue['@id']],
                'status': 'current',
            },
        ),
        status=201,
    )
    assert tissue['@id'] in res.json['@graph'][0]['samples']


@pytest.mark.parametrize('file_type', ['raw_matrix_file', 'processed_matrix_file'])
def test_matrix_file_patch_samples(testapp, other_lab, tissue, file_type):
    config = FILE_TYPE_CONFIGS[file_type]
    endpoint = config['endpoint']
    file_format = config['default_format']
    s3_path = config['s3_path']

    res = testapp.post_json(
        endpoint,
        _augment_matrix_file_post(
            file_type,
            {
                'lab': other_lab['@id'],
                'file_format': file_format,
                's3_uri': f's3://lattice-test-data/{s3_path}/patch-samples.{file_format}',
                'crc64nvme_base64': CRC64NVME_BASE64_VALID,
                'status': 'current',
            },
        ),
        status=201,
    )
    file_id = res.json['@graph'][0]['@id']
    patched = testapp.patch_json(
        file_id,
        {'samples': [tissue['@id']]},
        status=200,
    )
    assert tissue['@id'] in patched.json['@graph'][0]['samples']


def test_raw_matrix_file_required_processing_metadata(testapp, other_lab):
    testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'file_format': 'h5',
            'no_file_available': True,
            'status': 'current',
        },
        status=422,
    )


def test_raw_matrix_file_software_version_optional(testapp, other_lab):
    res = testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'file_format': 'h5',
            'no_file_available': True,
            'software': 'Cell Ranger',
            'genome_assembly': 'GRCh38',
            'is_multiplexed': False,
            'status': 'current',
        },
        status=201,
    )
    assert 'software_version' not in res.json['@graph'][0]


def test_raw_matrix_file_h5ad_format_accepted(testapp, other_lab):
    res = testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'file_format': 'h5ad',
            'no_file_available': True,
            'software': 'Cell Ranger',
            'software_version': '7.1.0',
            'genome_assembly': 'GRCh38',
            'is_multiplexed': False,
            'status': 'current',
        },
        status=201,
    )
    assert res.json['@graph'][0]['file_format'] == 'h5ad'


def test_processed_matrix_file_is_multiplexed_required(testapp, other_lab):
    testapp.post_json(
        '/processed_matrix_file',
        {
            'lab': other_lab['@id'],
            'file_format': 'h5ad',
            'no_file_available': True,
            'status': 'current',
        },
        status=422,
    )


def test_raw_matrix_file_is_multiplexed_true(testapp, other_lab):
    res = testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'file_format': 'h5',
            'no_file_available': True,
            'software': 'Cell Ranger',
            'software_version': '7.1.0',
            'genome_assembly': 'GRCh38',
            'is_multiplexed': True,
            'status': 'current',
        },
        status=201,
    )
    assert res.json['@graph'][0]['is_multiplexed'] is True


def test_processed_matrix_file_is_multiplexed_false(testapp, other_lab):
    res = testapp.post_json(
        '/processed_matrix_file',
        {
            'lab': other_lab['@id'],
            'file_format': 'h5ad',
            'no_file_available': True,
            'is_multiplexed': False,
            'status': 'current',
        },
        status=201,
    )
    assert res.json['@graph'][0]['is_multiplexed'] is False


def test_raw_matrix_file_rejects_genome_annotation(testapp, other_lab):
    testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'file_format': 'h5',
            'no_file_available': True,
            'status': 'current',
            **RAW_MATRIX_FILE_METADATA,
            'genome_annotation': 'GENCODE v44',
        },
        status=422,
    )


@pytest.mark.parametrize('missing_field', ['software', 'genome_assembly', 'is_multiplexed'])
def test_raw_matrix_file_missing_required_processing_field(
    testapp, other_lab, missing_field
):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'h5',
        'no_file_available': True,
        'status': 'current',
        **RAW_MATRIX_FILE_METADATA,
    }
    del item[missing_field]
    testapp.post_json('/raw_matrix_file', item, status=422)


def test_raw_matrix_file_genome_assembly_enum(testapp, other_lab):
    testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'file_format': 'h5',
            'no_file_available': True,
            'status': 'current',
            **RAW_MATRIX_FILE_METADATA,
            'genome_assembly': 'invalid_assembly',
        },
        status=422,
    )


@pytest.mark.parametrize('genome_assembly', ['GRCh38', 'GRCm39'])
def test_raw_matrix_file_genome_assembly_values(testapp, other_lab, genome_assembly):
    res = testapp.post_json(
        '/raw_matrix_file',
        {
            'lab': other_lab['@id'],
            'file_format': 'h5',
            'no_file_available': True,
            'status': 'current',
            **RAW_MATRIX_FILE_METADATA,
            'genome_assembly': genome_assembly,
        },
        status=201,
    )
    assert res.json['@graph'][0]['genome_assembly'] == genome_assembly


def test_raw_matrix_file_processing_metadata_persists(testapp, raw_matrix_file):
    res = testapp.get(raw_matrix_file['@id'])
    assert res.json['software'] == 'Cell Ranger'
    assert res.json['software_version'] == '7.1.0'
    assert res.json['genome_assembly'] == 'GRCh38'


def test_matrix_files_reverse_links(testapp, matrix_file_set, matrix_file_set_with_processed):
    raw_file = matrix_file_set['raw_matrix_files'][0]
    processed_file = matrix_file_set_with_processed['processed_matrix_files'][0]

    raw_res = testapp.get(raw_file).json
    assert matrix_file_set['@id'] in raw_res['matrix_file_sets']

    processed_res = testapp.get(processed_file).json
    assert matrix_file_set_with_processed['@id'] in processed_res['matrix_file_sets']
