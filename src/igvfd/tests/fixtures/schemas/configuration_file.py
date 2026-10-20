import pytest


@pytest.fixture
def configuration_file(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'csv',
        'content_type': 'cell ranger config',
        's3_uri': 's3://lattice-test-data/configuration/fixture-csv-001.csv',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'status': 'current',
    }
    return testapp.post_json('/configuration_file', item, status=201).json['@graph'][0]


@pytest.fixture
def configuration_file_with_description(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'csv',
        'content_type': 'cell ranger config',
        's3_uri': 's3://lattice-test-data/configuration/fixture-csv-002.csv',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'description': 'Test configuration file',
        'status': 'current',
    }
    return testapp.post_json('/configuration_file', item, status=201).json['@graph'][0]


@pytest.fixture
def configuration_file_with_aliases(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'csv',
        'content_type': 'cell ranger config',
        's3_uri': 's3://lattice-test-data/configuration/fixture-csv-003.csv',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'aliases': ['lattice:configuration-file-001'],
        'status': 'current',
    }
    return testapp.post_json('/configuration_file', item, status=201).json['@graph'][0]
