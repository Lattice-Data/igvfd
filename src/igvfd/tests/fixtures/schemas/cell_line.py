import pytest


@pytest.fixture
def cell_line(testapp, other_lab, human_donor, controlled_term):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term['@id']],
        'status': 'current',
    }
    return testapp.post_json('/cell_line', item, status=201).json['@graph'][0]


@pytest.fixture
def cell_line_with_description(testapp, other_lab, human_donor, controlled_term):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term['@id']],
        'description': 'Test cell line sample',
        'status': 'current',
    }
    return testapp.post_json('/cell_line', item, status=201).json['@graph'][0]


@pytest.fixture
def cell_line_with_aliases(testapp, other_lab, human_donor, controlled_term):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term['@id']],
        'aliases': ['lattice:cell-line-immortalized'],
        'status': 'current',
    }
    return testapp.post_json('/cell_line', item, status=201).json['@graph'][0]


@pytest.fixture
def cell_line_with_host(testapp, other_lab, human_donor, controlled_term, non_human_donor):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term['@id']],
        'host': non_human_donor['@id'],
        'host_tissue': controlled_term['@id'],
        'status': 'current',
    }
    return testapp.post_json('/cell_line', item, status=201).json['@graph'][0]
