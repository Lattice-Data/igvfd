import pytest


_RAW_MATRIX_METADATA = {
    'software': 'Cell Ranger',
    'software_version': '7.1.0',
    'genome_assembly': 'GRCh38',
}


@pytest.fixture
def raw_matrix_file(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'h5',
        's3_uri': 's3://lattice-test-data/matrix/fixture-raw-001.h5',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'status': 'current',
        **_RAW_MATRIX_METADATA,
    }
    return testapp.post_json('/raw_matrix_file', item, status=201).json['@graph'][0]


@pytest.fixture
def raw_matrix_file_with_description(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'h5',
        's3_uri': 's3://lattice-test-data/matrix/fixture-raw-002.h5',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'feature_keys': ['Ensembl gene ID', 'gene symbol'],
        'observation_count': 9000,
        'feature_counts': [
            {'feature_type': 'gene', 'feature_count': 17000},
        ],
        'description': 'Test raw matrix file',
        'status': 'current',
        **_RAW_MATRIX_METADATA,
    }
    return testapp.post_json('/raw_matrix_file', item, status=201).json['@graph'][0]


@pytest.fixture
def raw_matrix_file_with_samples(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'md5sum': 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6',
        'file_format': 'h5',
        's3_uri': 's3://lattice-test-data/matrix/fixture-raw-004.h5',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'feature_keys': ['crispr guide ID', 'hash oligo'],
        'observation_count': 7000,
        'feature_counts': [
            {'feature_type': 'guide capture', 'feature_count': 4000},
        ],
        'samples': [tissue['@id']],
        'status': 'current',
        **_RAW_MATRIX_METADATA,
    }
    return testapp.post_json('/raw_matrix_file', item, status=201).json['@graph'][0]


@pytest.fixture
def raw_matrix_file_with_aliases(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'h5',
        's3_uri': 's3://lattice-test-data/matrix/fixture-raw-003.h5',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'aliases': ['lattice:pytest-raw-matrix-file-001'],
        'status': 'current',
        **_RAW_MATRIX_METADATA,
    }
    return testapp.post_json('/raw_matrix_file', item, status=201).json['@graph'][0]
