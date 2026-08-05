import pytest


@pytest.fixture
def tabular_file(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'csv',
        'content_type': 'guide RNA sequences',
        'guides_signature': 'gsig1:set:n=8:5e2d1a7f9c04b836e71fa2d0c5b98436',
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
        'guides_signature': 'gsig1:set:n=16:a1b2c3d4e5f60718293a4b5c6d7e8f90',
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
        'guides_signature': 'gsig1:set:n=24:0f1e2d3c4b5a69788796a5b4c3d2e1f0',
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
        'guides_signature': 'gsig1:set:n=32:9c8b7a6f5e4d3c2b1a0918273645ac5d',
        's3_uri': 's3://lattice-test-data/tabular/fixture-tsv-002.tsv',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'status': 'current',
    }
    return testapp.post_json('/tabular_file', item, status=201).json['@graph'][0]
