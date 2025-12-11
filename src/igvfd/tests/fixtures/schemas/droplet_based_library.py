import pytest


@pytest.fixture
def droplet_based_library(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'status': 'current',
    }
    return testapp.post_json('/droplet_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def droplet_based_library_with_description(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'description': 'Test droplet-based library',
        'status': 'current',
    }
    return testapp.post_json('/droplet_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def droplet_based_library_with_aliases(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'aliases': ['lattice:droplet-library-basic'],
        'status': 'current',
    }
    return testapp.post_json('/droplet_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def droplet_based_library_with_chemistry_version(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'chemistry_version': '3\' v3',
        'status': 'current',
    }
    return testapp.post_json('/droplet_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def droplet_based_library_with_feature_types(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'feature_types': ['Gene Expression'],
        'status': 'current',
    }
    return testapp.post_json('/droplet_based_library', item, status=201).json['@graph'][0]
