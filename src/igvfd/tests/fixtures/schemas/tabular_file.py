import pytest


@pytest.fixture
def tabular_file(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'csv',
        'content_type': 'guide RNA sequences',
        's3_uri': 's3://lattice-test-data/tabular/fixture-csv-001.csv',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'status': 'current',
    }
    return testapp.post_json('/tabular_file', item, status=201).json['@graph'][0]


@pytest.fixture
def tabular_file_with_description(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'tsv',
        'content_type': 'guide RNA sequences',
        's3_uri': 's3://lattice-test-data/tabular/fixture-tsv-001.tsv',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'description': 'Test tabular file',
        'status': 'current',
    }
    return testapp.post_json('/tabular_file', item, status=201).json['@graph'][0]


@pytest.fixture
def tabular_file_with_aliases(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'csv',
        'content_type': 'guide RNA sequences',
        's3_uri': 's3://lattice-test-data/tabular/fixture-csv-002.csv',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'aliases': ['lattice:tabular-file-001'],
        'status': 'current',
    }
    return testapp.post_json('/tabular_file', item, status=201).json['@graph'][0]


@pytest.fixture
def tabular_file_tsv(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'tsv',
        'content_type': 'guide RNA sequences',
        's3_uri': 's3://lattice-test-data/tabular/fixture-tsv-002.tsv',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'status': 'current',
    }
    return testapp.post_json('/tabular_file', item, status=201).json['@graph'][0]
