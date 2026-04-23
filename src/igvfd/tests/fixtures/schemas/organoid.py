import pytest


@pytest.fixture
def organoid(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'status': 'current',
    }
    return testapp.post_json('/organoid', item, status=201).json['@graph'][0]


@pytest.fixture
def organoid_with_description(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'description': 'Test organoid sample',
        'status': 'current',
    }
    return testapp.post_json('/organoid', item, status=201).json['@graph'][0]


@pytest.fixture
def organoid_with_aliases(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'aliases': ['lattice:organoid-brain-model'],
        'status': 'current',
    }
    return testapp.post_json('/organoid', item, status=201).json['@graph'][0]
