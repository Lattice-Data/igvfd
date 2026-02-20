import pytest


@pytest.fixture
def treatment(testapp, other_lab, controlled_term_chebi):
    item = {
        'lab': other_lab['@id'],
        'ontological_term': controlled_term_chebi['@id'],
        'status': 'current',
    }
    return testapp.post_json('/treatment', item, status=201).json['@graph'][0]


@pytest.fixture
def treatment_with_aliases(testapp, other_lab, controlled_term_chebi):
    item = {
        'lab': other_lab['@id'],
        'ontological_term': controlled_term_chebi['@id'],
        'aliases': ['lattice:treatment-water'],
        'status': 'current',
    }
    return testapp.post_json('/treatment', item, status=201).json['@graph'][0]


@pytest.fixture
def treatment_with_description(testapp, other_lab, controlled_term_chebi):
    item = {
        'lab': other_lab['@id'],
        'ontological_term': controlled_term_chebi['@id'],
        'description': 'Water vehicle control treatment',
        'status': 'current',
    }
    return testapp.post_json('/treatment', item, status=201).json['@graph'][0]
