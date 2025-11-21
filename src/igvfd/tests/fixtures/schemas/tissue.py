import pytest


@pytest.fixture
def tissue(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'status': 'current',
    }
    return testapp.post_json('/tissue', item, status=201).json['@graph'][0]


@pytest.fixture
def tissue_with_description(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'description': 'Test tissue sample',
        'status': 'current',
    }
    return testapp.post_json('/tissue', item, status=201).json['@graph'][0]


@pytest.fixture
def tissue_with_aliases(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'aliases': ['lattice:tissue-brain-coronal'],
        'status': 'current',
    }
    return testapp.post_json('/tissue', item, status=201).json['@graph'][0]


@pytest.fixture
def tissue_with_preservation_method(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'preservation_method': 'frozen',
        'status': 'current',
    }
    return testapp.post_json('/tissue', item, status=201).json['@graph'][0]


@pytest.fixture
def tissue_with_thickness(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'thickness': 5.0,
        'thickness_units': 'mm',
        'status': 'current',
    }
    return testapp.post_json('/tissue', item, status=201).json['@graph'][0]
