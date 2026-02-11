import pytest


@pytest.fixture
def sequencing_run_single_end(testapp, other_lab, sequence_file):
    item = {
        'lab': other_lab['@id'],
        'run_cardinality': 'single-end',
        'read1': sequence_file['@id'],
        'status': 'current',
    }
    return testapp.post_json('/sequencing_run', item, status=201).json['@graph'][0]


@pytest.fixture
def sequencing_run_paired_end(testapp, other_lab, sequence_file, sequence_file_with_description):
    item = {
        'lab': other_lab['@id'],
        'run_cardinality': 'paired-end',
        'read1': sequence_file['@id'],
        'read2': sequence_file_with_description['@id'],
        'status': 'current',
    }
    return testapp.post_json('/sequencing_run', item, status=201).json['@graph'][0]


@pytest.fixture
def sequencing_run_with_aliases(testapp, other_lab, sequence_file, sequence_file_with_description):
    item = {
        'lab': other_lab['@id'],
        'run_cardinality': 'paired-end',
        'read1': sequence_file['@id'],
        'read2': sequence_file_with_description['@id'],
        'aliases': ['lattice:sequencing-run-001'],
        'status': 'current',
    }
    return testapp.post_json('/sequencing_run', item, status=201).json['@graph'][0]


@pytest.fixture
def sequencing_run_with_platform(testapp, other_lab, sequence_file, sequence_file_with_description):
    item = {
        'lab': other_lab['@id'],
        'run_cardinality': 'paired-end',
        'read1': sequence_file['@id'],
        'read2': sequence_file_with_description['@id'],
        'sequencing_platform': 'Illumina NextSeq 1000',
        'status': 'current',
    }
    return testapp.post_json('/sequencing_run', item, status=201).json['@graph'][0]
