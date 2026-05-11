import pytest


@pytest.fixture
def human_donor(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'sex': 'unspecified',
        'cxg_donor_id': 'lattice:test-cxg-human-001',
        'author_metadata': {
            'submitter_field': 'human donor fixture'
        },
        'status': 'current',
    }
    return testapp.post_json('/human_donor', item, status=201).json['@graph'][0]


@pytest.fixture
def human_donor_with_description(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'sex': 'unspecified',
        'cxg_donor_id': 'lattice:test-cxg-human-003',
        'description': 'Test human donor',
    }
    return testapp.post_json('/human_donor', item, status=201).json['@graph'][0]


@pytest.fixture
def human_donor_with_aliases(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'sex': 'unspecified',
        'aliases': ['lattice:pytest-human-donor-summary-alias'],
        'cxg_donor_id': 'lattice:test-cxg-human-alias',
        'status': 'current',
    }
    return testapp.post_json('/human_donor', item, status=201).json['@graph'][0]


@pytest.fixture
def human_donor_with_ethnicity(testapp, other_lab, controlled_term_ethnicity):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'sex': 'female',
        'cxg_donor_id': 'lattice:test-cxg-human-004',
        'ethnicity': controlled_term_ethnicity['@id'],
        'status': 'current',
    }
    return testapp.post_json('/human_donor', item, status=201).json['@graph'][0]
