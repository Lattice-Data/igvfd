import pytest


@pytest.fixture
def sequence_file(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'fastq',
        's3_uri': 's3://lattice-test-data/sequence/fixture-fastq-001.fastq.gz',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'read_count': 15000000,
        'status': 'current',
    }
    return testapp.post_json('/sequence_file', item, status=201).json['@graph'][0]


@pytest.fixture
def sequence_file_with_description(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'fastq',
        's3_uri': 's3://lattice-test-data/sequence/fixture-fastq-002.fastq.gz',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'read_count': 16000000,
        'description': 'Test sequence file',
        'status': 'current',
    }
    return testapp.post_json('/sequence_file', item, status=201).json['@graph'][0]


@pytest.fixture
def sequence_file_with_aliases(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'fastq',
        's3_uri': 's3://lattice-test-data/sequence/fixture-fastq-003.fastq.gz',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'read_count': 17000000,
        'aliases': ['lattice:sequence-file-001'],
        'status': 'current',
    }
    return testapp.post_json('/sequence_file', item, status=201).json['@graph'][0]


@pytest.fixture
def sequence_file_cram(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'cram',
        's3_uri': 's3://lattice-test-data/sequence/fixture-cram-001.cram',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'read_count': 9000000,
        'status': 'current',
    }
    return testapp.post_json('/sequence_file', item, status=201).json['@graph'][0]
