import pytest


@pytest.fixture
def matrix_file_set(testapp, other_lab, raw_matrix_file, sequence_file_set_illumina_single_end):
    item = {
        'lab': other_lab['@id'],
        'experiment_ids': ['EXP-001'],
        'raw_matrix_files': [raw_matrix_file['@id']],
        'source_sequence_file_sets': [sequence_file_set_illumina_single_end['@id']],
        'status': 'current',
    }
    return testapp.post_json('/matrix_file_set', item, status=201).json['@graph'][0]


@pytest.fixture
def matrix_file_set_with_processed(testapp, other_lab, processed_matrix_file,
                                   sequence_file_set_illumina_single_end):
    item = {
        'lab': other_lab['@id'],
        'experiment_ids': ['EXP-002'],
        'processed_matrix_files': [processed_matrix_file['@id']],
        'source_sequence_file_sets': [sequence_file_set_illumina_single_end['@id']],
        'status': 'current',
    }
    return testapp.post_json('/matrix_file_set', item, status=201).json['@graph'][0]


@pytest.fixture
def matrix_file_set_with_aliases(testapp, other_lab, raw_matrix_file,
                                 sequence_file_set_illumina_single_end):
    item = {
        'lab': other_lab['@id'],
        'experiment_ids': ['EXP-003'],
        'raw_matrix_files': [raw_matrix_file['@id']],
        'source_sequence_file_sets': [sequence_file_set_illumina_single_end['@id']],
        'aliases': ['lattice:matrix-file-set-001'],
        'status': 'current',
    }
    return testapp.post_json('/matrix_file_set', item, status=201).json['@graph'][0]


@pytest.fixture
def matrix_file_set_with_multiple_experiment_ids(testapp, other_lab, raw_matrix_file,
                                                 sequence_file_set_illumina_single_end):
    item = {
        'lab': other_lab['@id'],
        'experiment_ids': ['EXP-004', 'EXP-005'],
        'raw_matrix_files': [raw_matrix_file['@id']],
        'source_sequence_file_sets': [sequence_file_set_illumina_single_end['@id']],
        'status': 'current',
    }
    return testapp.post_json('/matrix_file_set', item, status=201).json['@graph'][0]


@pytest.fixture
def matrix_file_set_with_all_fields(testapp, other_lab, raw_matrix_file, processed_matrix_file,
                                    sequence_file_set_illumina_single_end):
    item = {
        'lab': other_lab['@id'],
        'experiment_ids': ['EXP-006'],
        'raw_matrix_files': [raw_matrix_file['@id']],
        'processed_matrix_files': [processed_matrix_file['@id']],
        'source_sequence_file_sets': [sequence_file_set_illumina_single_end['@id']],
        'software': 'Cell Ranger',
        'software_version': '7.1.0',
        'genome_assembly': 'GRCh38',
        'genome_annotation': 'GENCODE v44',
        'description': 'Test matrix file set with all fields',
        'aliases': ['lattice:matrix-file-set-full-001'],
        'status': 'current',
    }
    return testapp.post_json('/matrix_file_set', item, status=201).json['@graph'][0]
