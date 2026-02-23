import pytest


@pytest.fixture
def tabular_file(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'csv',
        's3_uri': 's3://lattice-test-data/tabular/fixture-csv-001.csv',
        'status': 'current',
    }
    return testapp.post_json('/tabular_file', item, status=201).json['@graph'][0]


@pytest.fixture
def tabular_file_with_description(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6',
        'file_format': 'tsv',
        's3_uri': 's3://lattice-test-data/tabular/fixture-tsv-001.tsv',
        'description': 'Test tabular file',
        'status': 'current',
    }
    return testapp.post_json('/tabular_file', item, status=201).json['@graph'][0]


@pytest.fixture
def tabular_file_with_aliases(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': 'f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6',
        'file_format': 'csv',
        's3_uri': 's3://lattice-test-data/tabular/fixture-csv-002.csv',
        'aliases': ['lattice:tabular-file-001'],
        'status': 'current',
    }
    return testapp.post_json('/tabular_file', item, status=201).json['@graph'][0]


@pytest.fixture
def tabular_file_tsv(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': '1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d',
        'file_format': 'tsv',
        's3_uri': 's3://lattice-test-data/tabular/fixture-tsv-002.tsv',
        'status': 'current',
    }
    return testapp.post_json('/tabular_file', item, status=201).json['@graph'][0]
