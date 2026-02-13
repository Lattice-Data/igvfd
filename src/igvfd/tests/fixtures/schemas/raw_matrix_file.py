import pytest


@pytest.fixture
def raw_matrix_file(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': 'c4ca4238a0b923820dcc509a6f75849b',
        'file_format': 'h5',
        's3_uri': 's3://lattice-test-data/matrix/fixture-raw-001.h5',
        'status': 'current',
    }
    return testapp.post_json('/raw_matrix_file', item, status=201).json['@graph'][0]


@pytest.fixture
def raw_matrix_file_with_description(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': 'c81e728d9d4c2f636f067f89cc14862c',
        'file_format': 'h5',
        's3_uri': 's3://lattice-test-data/matrix/fixture-raw-002.h5',
        'feature_keys': ['Ensembl gene ID', 'gene symbol'],
        'observation_count': 9000,
        'feature_counts': [
            {'feature_type': 'gene', 'feature_count': 17000},
        ],
        'description': 'Test raw matrix file',
        'status': 'current',
    }
    return testapp.post_json('/raw_matrix_file', item, status=201).json['@graph'][0]


@pytest.fixture
def raw_matrix_file_with_aliases(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': 'eccbc87e4b5ce2fe28308fd9f2a7baf3',
        'file_format': 'h5',
        's3_uri': 's3://lattice-test-data/matrix/fixture-raw-003.h5',
        'aliases': ['lattice:raw-matrix-file-001'],
        'status': 'current',
    }
    return testapp.post_json('/raw_matrix_file', item, status=201).json['@graph'][0]
