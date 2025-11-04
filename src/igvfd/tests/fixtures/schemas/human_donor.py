import pytest


@pytest.fixture
def human_donor(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'status': 'current',
    }
    return testapp.post_json('/human_donor', item, status=201).json['@graph'][0]


@pytest.fixture
def human_donor_with_description(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'description': 'Test human donor',
        'status': 'current',
    }
    return testapp.post_json('/human_donor', item, status=201).json['@graph'][0]


@pytest.fixture
def human_donor_with_aliases(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'aliases': ['lattice:test-donor-1', 'lattice:test-donor-alias'],
        'status': 'current',
    }
    return testapp.post_json('/human_donor', item, status=201).json['@graph'][0]


@pytest.fixture
def human_donor_with_ethnicity(testapp, other_lab, controlled_term_ethnicity):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'ethnicity': controlled_term_ethnicity['@id'],
        'status': 'current',
    }
    return testapp.post_json('/human_donor', item, status=201).json['@graph'][0]
