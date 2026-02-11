import pytest


@pytest.fixture
def sequence_file_set_illumina_single_end(testapp, other_lab, sequence_file, droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'library': droplet_based_library['@id'],
        'run_cardinality': 'single-end',
        'read1': sequence_file['@id'],
        'status': 'current',
    }
    return testapp.post_json('/sequence_file_set', item, status=201).json['@graph'][0]


@pytest.fixture
def sequence_file_set_illumina_paired_end(testapp, other_lab, sequence_file, sequence_file_with_description, droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'library': droplet_based_library['@id'],
        'run_cardinality': 'paired-end',
        'read1': sequence_file['@id'],
        'read2': sequence_file_with_description['@id'],
        'status': 'current',
    }
    return testapp.post_json('/sequence_file_set', item, status=201).json['@graph'][0]


@pytest.fixture
def sequence_file_set_ultima(testapp, other_lab, sequence_file_cram, droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'library': droplet_based_library['@id'],
        'run_cardinality': 'single-end',
        'untrimmed_cram': sequence_file_cram['@id'],
        'sequencing_platform': 'Ultima Genomics UG 100',
        'status': 'current',
    }
    return testapp.post_json('/sequence_file_set', item, status=201).json['@graph'][0]


@pytest.fixture
def sequence_file_set_with_aliases(testapp, other_lab, sequence_file, droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'library': droplet_based_library['@id'],
        'run_cardinality': 'single-end',
        'read1': sequence_file['@id'],
        'aliases': ['lattice:sequence-file-set-001'],
        'status': 'current',
    }
    return testapp.post_json('/sequence_file_set', item, status=201).json['@graph'][0]


@pytest.fixture
def sequence_file_set_with_cro_order(testapp, other_lab, sequence_file, droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'library': droplet_based_library['@id'],
        'run_cardinality': 'single-end',
        'read1': sequence_file['@id'],
        'CRO_order': 'AN00012345',
        'status': 'current',
    }
    return testapp.post_json('/sequence_file_set', item, status=201).json['@graph'][0]
