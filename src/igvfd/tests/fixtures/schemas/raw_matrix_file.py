import pytest


@pytest.fixture
def raw_matrix_file(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'file_format': 'h5',
        's3_uri': 's3://lattice-test-data/matrix/fixture-raw-001.h5',
        'status': 'current',
    }
    return testapp.post_json('/raw_matrix_file', item, status=201).json['@graph'][0]


@pytest.fixture
def raw_matrix_file_with_description(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
        'file_format': 'h5',
        's3_uri': 's3://lattice-test-data/matrix/fixture-raw-002.h5',
        'description': 'Test raw matrix file',
        'status': 'current',
    }
    return testapp.post_json('/raw_matrix_file', item, status=201).json['@graph'][0]


@pytest.fixture
def raw_matrix_file_with_aliases(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': 'cccccccccccccccccccccccccccccccc',
        'file_format': 'h5',
        's3_uri': 's3://lattice-test-data/matrix/fixture-raw-003.h5',
        'aliases': ['lattice:raw-matrix-file-001'],
        'status': 'current',
    }
    return testapp.post_json('/raw_matrix_file', item, status=201).json['@graph'][0]
