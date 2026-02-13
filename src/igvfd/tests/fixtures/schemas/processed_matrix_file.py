import pytest


@pytest.fixture
def processed_matrix_file(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': 'a87ff679a2f3e71d9181a67b7542122c',
        'file_format': 'h5ad',
        's3_uri': 's3://lattice-test-data/matrix/fixture-processed-001.h5ad',
        'status': 'current',
    }
    return testapp.post_json('/processed_matrix_file', item, status=201).json['@graph'][0]


@pytest.fixture
def processed_matrix_file_with_description(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': 'e4da3b7fbbce2345d7772b0674a318d5',
        'file_format': 'h5ad',
        's3_uri': 's3://lattice-test-data/matrix/fixture-processed-002.h5ad',
        'feature_keys': ['Ensembl gene ID', 'gene symbol'],
        'observation_count': 8500,
        'feature_counts': [
            {'feature_type': 'gene', 'feature_count': 16000},
        ],
        'description': 'Test processed matrix file',
        'status': 'current',
    }
    return testapp.post_json('/processed_matrix_file', item, status=201).json['@graph'][0]


@pytest.fixture
def processed_matrix_file_with_aliases(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': '1679091c5a880faf6fb5e6087eb1b2dc',
        'file_format': 'h5ad',
        's3_uri': 's3://lattice-test-data/matrix/fixture-processed-003.h5ad',
        'aliases': ['lattice:processed-matrix-file-001'],
        'status': 'current',
    }
    return testapp.post_json('/processed_matrix_file', item, status=201).json['@graph'][0]
