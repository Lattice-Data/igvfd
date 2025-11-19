import pytest


@pytest.fixture
def in_vivo_system(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'classification': 'xenograft',
        'status': 'current',
    }
    return testapp.post_json('/in_vivo_system', item, status=201).json['@graph'][0]


@pytest.fixture
def in_vivo_system_with_description(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'classification': 'xenograft',
        'description': 'Test in vivo system sample',
        'status': 'current',
    }
    return testapp.post_json('/in_vivo_system', item, status=201).json['@graph'][0]


@pytest.fixture
def in_vivo_system_with_aliases(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'classification': 'xenograft',
        'aliases': ['lattice:test-in-vivo-1', 'lattice:test-in-vivo-alias'],
        'status': 'current',
    }
    return testapp.post_json('/in_vivo_system', item, status=201).json['@graph'][0]


@pytest.fixture
def in_vivo_system_with_host(testapp, other_lab, human_donor, controlled_term_brain, non_human_donor):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'classification': 'xenograft',
        'host': non_human_donor['@id'],
        'status': 'current',
    }
    return testapp.post_json('/in_vivo_system', item, status=201).json['@graph'][0]


@pytest.fixture
def in_vivo_system_with_classification(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'classification': 'xenograft',
        'status': 'current',
    }
    return testapp.post_json('/in_vivo_system', item, status=201).json['@graph'][0]
