import pytest


@pytest.fixture
def genetic_modification(testapp):
    item = {
        'modality': 'knockout',
        'status': 'current',
    }
    return testapp.post_json('/genetic_modification', item, status=201).json['@graph'][0]


@pytest.fixture
def genetic_modification_activation(testapp):
    item = {
        'modality': 'activation',
        'status': 'current',
    }
    return testapp.post_json('/genetic_modification', item, status=201).json['@graph'][0]


@pytest.fixture
def genetic_modification_with_description(testapp):
    item = {
        'modality': 'interference',
        'description': 'CRISPRi-based gene silencing modification.',
        'status': 'current',
    }
    return testapp.post_json('/genetic_modification', item, status=201).json['@graph'][0]


@pytest.fixture
def genetic_modification_with_aliases(testapp):
    item = {
        'modality': 'cutting',
        'aliases': ['lattice:gm-test-1', 'lattice:gm-crispr-cut'],
        'status': 'current',
    }
    return testapp.post_json('/genetic_modification', item, status=201).json['@graph'][0]


@pytest.fixture
def genetic_modification_base_editing(testapp):
    item = {
        'modality': 'base editing',
        'description': 'Base editing modification for point mutations.',
        'status': 'current',
    }
    return testapp.post_json('/genetic_modification', item, status=201).json['@graph'][0]


@pytest.fixture
def genetic_modification_prime_editing(testapp):
    item = {
        'modality': 'prime editing',
        'description': 'Prime editing modification for precise genome editing.',
        'status': 'current',
    }
    return testapp.post_json('/genetic_modification', item, status=201).json['@graph'][0]
