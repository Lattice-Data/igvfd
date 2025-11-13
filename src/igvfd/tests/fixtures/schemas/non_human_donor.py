import pytest


@pytest.fixture
def non_human_donor(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Mus musculus',
        'status': 'current',
    }
    return testapp.post_json('/non_human_donor', item, status=201).json['@graph'][0]


@pytest.fixture
def non_human_donor_with_description(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Mus musculus',
        'description': 'Test non human donor',
        'status': 'current',
    }
    return testapp.post_json('/non_human_donor', item, status=201).json['@graph'][0]


@pytest.fixture
def non_human_donor_with_aliases(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Mus musculus',
        'aliases': ['lattice:test-non-human-donor-1', 'lattice:test-non-human-donor-alias'],
        'status': 'current',
    }
    return testapp.post_json('/non_human_donor', item, status=201).json['@graph'][0]
