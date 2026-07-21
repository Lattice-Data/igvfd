import pytest


@pytest.fixture
def plate_based_library(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'status': 'current',
    }
    return testapp.post_json('/plate_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def plate_based_library_with_description(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'description': 'Test plate-based library',
        'status': 'current',
    }
    return testapp.post_json('/plate_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def plate_based_library_with_aliases(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'aliases': ['lattice:pytest-plate-library-basic'],
        'status': 'current',
    }
    return testapp.post_json('/plate_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def plate_based_library_with_feature_types(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'feature_types': ['Gene Expression'],
        'status': 'current',
    }
    return testapp.post_json('/plate_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def plate_based_library_dual(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'dual',
        'status': 'current',
    }
    return testapp.post_json('/plate_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def plate_based_library_dual_with_linked_library(
    testapp, other_lab, tissue, plate_based_library
):
    """Dual library linked to a partner (acyclic; partner is created first)."""
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'dual',
        'linked_libraries': [plate_based_library['@id']],
        'status': 'current',
    }
    return testapp.post_json('/plate_based_library', item, status=201).json['@graph'][0]


@pytest.fixture
def plate_based_library_with_library_construction_technology(testapp, other_lab, tissue, controlled_term_efo):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'library_construction_technology': controlled_term_efo['@id'],
        'status': 'current',
    }
    return testapp.post_json('/plate_based_library', item, status=201).json['@graph'][0]
