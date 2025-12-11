import pytest


@pytest.fixture
def plate_based_library(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'status': 'current',
    }
    return testapp.post_json('/plate_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def plate_based_library_with_description(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'description': 'Test plate-based library',
        'status': 'current',
    }
    return testapp.post_json('/plate_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def plate_based_library_with_aliases(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'aliases': ['lattice:plate-library-basic'],
        'status': 'current',
    }
    return testapp.post_json('/plate_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def plate_based_library_with_kit_version(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'kit_version': 'QuantumScale Single Cell RNA',
        'status': 'current',
    }
    return testapp.post_json('/plate_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def plate_based_library_with_indexing_rounds(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'indexing_rounds': 3,
        'status': 'current',
    }
    return testapp.post_json('/plate_based_library', item, status=201).json['@graph'][0]
