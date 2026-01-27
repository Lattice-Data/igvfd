import pytest


@pytest.fixture
def primary_cell_culture(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'status': 'current',
    }
    return testapp.post_json('/primary_cell_culture', item, status=201).json['@graph'][0]


@pytest.fixture
def primary_cell_culture_with_description(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'description': 'Test primary cell culture sample',
        'status': 'current',
    }
    return testapp.post_json('/primary_cell_culture', item, status=201).json['@graph'][0]


@pytest.fixture
def primary_cell_culture_with_aliases(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'aliases': ['lattice:primary-cell-passage-3'],
        'status': 'current',
    }
    return testapp.post_json('/primary_cell_culture', item, status=201).json['@graph'][0]


@pytest.fixture
def primary_cell_culture_with_passage_number(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'passage_number': 5,
        'status': 'current',
    }
    return testapp.post_json('/primary_cell_culture', item, status=201).json['@graph'][0]
