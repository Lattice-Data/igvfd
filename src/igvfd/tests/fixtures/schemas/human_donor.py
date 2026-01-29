import pytest


@pytest.fixture
def human_donor(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'sex': 'unspecified',
        'status': 'current',
    }
    return testapp.post_json('/human_donor', item, status=201).json['@graph'][0]


@pytest.fixture
def human_donor_with_description(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'sex': 'unspecified',
        'description': 'Test human donor',
        'status': 'current',
    }
    return testapp.post_json('/human_donor', item, status=201).json['@graph'][0]


@pytest.fixture
def human_donor_with_aliases(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'sex': 'unspecified',
        'aliases': ['lattice:human-donor-european'],
        'status': 'current',
    }
    return testapp.post_json('/human_donor', item, status=201).json['@graph'][0]


@pytest.fixture
def human_donor_with_ethnicity(testapp, other_lab, controlled_term_ethnicity):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'sex': 'female',
        'ethnicity': controlled_term_ethnicity['@id'],
        'status': 'current',
    }
    return testapp.post_json('/human_donor', item, status=201).json['@graph'][0]
