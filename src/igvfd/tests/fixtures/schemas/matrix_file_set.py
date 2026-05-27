import pytest


@pytest.fixture
def matrix_file_set(testapp, other_lab, raw_matrix_file):
    item = {
        'lab': other_lab['@id'],
        'raw_matrix_files': [raw_matrix_file['@id']],
        'status': 'current',
    }
    return testapp.post_json('/matrix_file_set', item, status=201).json['@graph'][0]


@pytest.fixture
def matrix_file_set_with_processed(testapp, other_lab, processed_matrix_file):
    item = {
        'lab': other_lab['@id'],
        'processed_matrix_files': [processed_matrix_file['@id']],
        'status': 'current',
    }
    return testapp.post_json('/matrix_file_set', item, status=201).json['@graph'][0]


@pytest.fixture
def matrix_file_set_with_aliases(testapp, other_lab, raw_matrix_file):
    item = {
        'lab': other_lab['@id'],
        'raw_matrix_files': [raw_matrix_file['@id']],
        'aliases': ['lattice:matrix-file-set-001'],
        'status': 'current',
    }
    return testapp.post_json('/matrix_file_set', item, status=201).json['@graph'][0]


@pytest.fixture
def matrix_file_set_with_all_fields(testapp, other_lab, raw_matrix_file, processed_matrix_file):
    item = {
        'lab': other_lab['@id'],
        'raw_matrix_files': [raw_matrix_file['@id']],
        'processed_matrix_files': [processed_matrix_file['@id']],
        'description': 'Test matrix file set with all fields',
        'aliases': ['lattice:matrix-file-set-full-001'],
        'status': 'current',
    }
    return testapp.post_json('/matrix_file_set', item, status=201).json['@graph'][0]
