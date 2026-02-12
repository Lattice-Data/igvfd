import pytest


@pytest.fixture
def processed_matrix_file(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': 'dddddddddddddddddddddddddddddddd',
        'file_format': 'h5ad',
        's3_uri': 's3://lattice-test-data/matrix/fixture-processed-001.h5ad',
        'status': 'current',
    }
    return testapp.post_json('/processed_matrix_file', item, status=201).json['@graph'][0]


@pytest.fixture
def processed_matrix_file_with_description(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
        'file_format': 'h5ad',
        's3_uri': 's3://lattice-test-data/matrix/fixture-processed-002.h5ad',
        'description': 'Test processed matrix file',
        'status': 'current',
    }
    return testapp.post_json('/processed_matrix_file', item, status=201).json['@graph'][0]


@pytest.fixture
def processed_matrix_file_with_aliases(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': 'ffffffffffffffffffffffffffffffff',
        'file_format': 'h5ad',
        's3_uri': 's3://lattice-test-data/matrix/fixture-processed-003.h5ad',
        'aliases': ['lattice:processed-matrix-file-001'],
        'status': 'current',
    }
    return testapp.post_json('/processed_matrix_file', item, status=201).json['@graph'][0]
