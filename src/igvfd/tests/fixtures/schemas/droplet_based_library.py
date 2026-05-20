import pytest


@pytest.fixture
def droplet_based_library(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'status': 'current',
    }
    return testapp.post_json('/droplet_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def droplet_based_library_with_description(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'description': 'Test droplet-based library',
        'status': 'current',
    }
    return testapp.post_json('/droplet_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def droplet_based_library_with_aliases(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'aliases': ['lattice:pytest-droplet-library-basic'],
        'status': 'current',
    }
    return testapp.post_json('/droplet_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def droplet_based_library_with_chemistry_version(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'chemistry_version': '3\' v3',
        'status': 'current',
    }
    return testapp.post_json('/droplet_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def droplet_based_library_with_feature_types(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'feature_types': ['Gene Expression'],
        'status': 'current',
    }
    return testapp.post_json('/droplet_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def droplet_based_library_dual(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'dual',
        'status': 'current',
    }
    return testapp.post_json('/droplet_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def droplet_based_library_dual_with_linked_library(
    testapp, other_lab, tissue, droplet_based_library
):
    """Dual library linked to a partner (acyclic; partner is created first)."""
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'dual',
        'linked_libraries': [droplet_based_library['@id']],
        'status': 'current',
    }
    return testapp.post_json('/droplet_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def droplet_based_library_dual_pair(testapp, other_lab, tissue):
    """Two dual libraries where the second links to the first (for pairing tests)."""
    base_item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'dual',
        'status': 'current',
    }
    partner = testapp.post_json('/droplet_based_library', base_item, status=201).json['@graph'][0]
    linked_item = {
        **base_item,
        'linked_libraries': [partner['@id']],
    }
    linked = testapp.post_json('/droplet_based_library', linked_item, status=201).json['@graph'][0]
    return {'partner': partner, 'linked': linked}


@pytest.fixture
def droplet_based_library_with_library_construction_technology(testapp, other_lab, tissue, controlled_term_efo):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'library_construction_technology': controlled_term_efo['@id'],
        'status': 'current',
    }
    return testapp.post_json('/droplet_based_library', item, status=201).json['@graph'][0]
