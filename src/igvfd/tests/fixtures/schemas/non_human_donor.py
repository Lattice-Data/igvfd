import pytest


@pytest.fixture
def non_human_donor(testapp, other_lab, taxon_mus_musculus):
    item = {
        'lab': other_lab['@id'],
        'taxa': taxon_mus_musculus['@id'],
        'cxg_donor_id': 'lattice:test-cxg-nhd-mouse-001',
        'author_metadata': {
            'submitter_field': 'non human donor fixture'
        },
        'status': 'current',
    }
    return testapp.post_json('/non_human_donor', item, status=201).json['@graph'][0]


@pytest.fixture
def non_human_donor_with_description(testapp, other_lab, taxon_mus_musculus):
    item = {
        'lab': other_lab['@id'],
        'taxa': taxon_mus_musculus['@id'],
        'cxg_donor_id': 'lattice:test-cxg-nhd-mouse-002',
        'description': 'Test non human donor',
        'status': 'current',
    }
    return testapp.post_json('/non_human_donor', item, status=201).json['@graph'][0]


@pytest.fixture
def non_human_donor_with_aliases(testapp, other_lab, taxon_mus_musculus):
    item = {
        'lab': other_lab['@id'],
        'taxa': taxon_mus_musculus['@id'],
        'aliases': ['lattice:test-non-human-donor-1', 'lattice:test-non-human-donor-alias'],
        'cxg_donor_id': 'lattice:test-cxg-nhd-mouse-003',
        'status': 'current',
    }
    return testapp.post_json('/non_human_donor', item, status=201).json['@graph'][0]
