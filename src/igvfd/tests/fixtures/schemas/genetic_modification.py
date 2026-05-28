import pytest


@pytest.fixture
def genetic_modification(testapp):
    item = {
        'strategy': 'knockout screen',
        'status': 'current',
    }
    return testapp.post_json('/genetic_modification', item, status=201).json['@graph'][0]


@pytest.fixture
def genetic_modification_activation(testapp):
    item = {
        'strategy': 'activation screen',
        'status': 'current',
    }
    return testapp.post_json('/genetic_modification', item, status=201).json['@graph'][0]


@pytest.fixture
def genetic_modification_with_description(testapp):
    item = {
        'strategy': 'interference screen',
        'description': 'CRISPRi-based gene silencing modification.',
        'status': 'current',
    }
    return testapp.post_json('/genetic_modification', item, status=201).json['@graph'][0]


@pytest.fixture
def genetic_modification_with_aliases(testapp):
    item = {
        'strategy': 'cutting screen',
        'aliases': ['lattice:gm-test-1', 'lattice:gm-crispr-cut'],
        'status': 'current',
    }
    return testapp.post_json('/genetic_modification', item, status=201).json['@graph'][0]


@pytest.fixture
def genetic_modification_base_editing(testapp):
    item = {
        'strategy': 'base editing screen',
        'description': 'Base editing modification for point mutations.',
        'status': 'current',
    }
    return testapp.post_json('/genetic_modification', item, status=201).json['@graph'][0]


@pytest.fixture
def genetic_modification_prime_editing(testapp):
    item = {
        'strategy': 'prime editing screen',
        'description': 'Prime editing modification for precise genome editing.',
        'status': 'current',
    }
    return testapp.post_json('/genetic_modification', item, status=201).json['@graph'][0]


@pytest.fixture
def genetic_modification_knockout_mutation(testapp):
    item = {
        'strategy': 'knockout mutation',
        'status': 'current',
    }
    return testapp.post_json('/genetic_modification', item, status=201).json['@graph'][0]
