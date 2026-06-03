import pytest


@pytest.fixture
def processed_matrix_file(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'h5ad',
        's3_uri': 's3://lattice-test-data/matrix/fixture-processed-001.h5ad',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'is_multiplexed': False,
        'status': 'current',
    }
    return testapp.post_json('/processed_matrix_file', item, status=201).json['@graph'][0]


@pytest.fixture
def processed_matrix_file_with_description(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'h5ad',
        's3_uri': 's3://lattice-test-data/matrix/fixture-processed-002.h5ad',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'feature_keys': ['Ensembl gene ID', 'gene symbol'],
        'observation_count': 8500,
        'feature_counts': [
            {'feature_type': 'gene', 'feature_count': 16000},
        ],
        'description': 'Test processed matrix file',
        'is_multiplexed': False,
        'status': 'current',
    }
    return testapp.post_json('/processed_matrix_file', item, status=201).json['@graph'][0]


@pytest.fixture
def processed_matrix_file_with_samples(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'md5sum': 'b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7',
        'file_format': 'h5ad',
        's3_uri': 's3://lattice-test-data/matrix/fixture-processed-004.h5ad',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'feature_keys': ['Ensembl gene ID'],
        'observation_count': 6500,
        'feature_counts': [
            {'feature_type': 'guide capture', 'feature_count': 3500},
        ],
        'samples': [tissue['@id']],
        'is_multiplexed': False,
        'status': 'current',
    }
    return testapp.post_json('/processed_matrix_file', item, status=201).json['@graph'][0]


@pytest.fixture
def processed_matrix_file_with_aliases(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'h5ad',
        's3_uri': 's3://lattice-test-data/matrix/fixture-processed-003.h5ad',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'aliases': ['lattice:pytest-processed-matrix-file-001'],
        'is_multiplexed': False,
        'status': 'current',
    }
    return testapp.post_json('/processed_matrix_file', item, status=201).json['@graph'][0]
