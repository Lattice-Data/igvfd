import pytest


@pytest.fixture
def experimental_condition_temperature(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'condition': 'temperature',
        'value': 37,
        'units': 'celsius',
        'status': 'current',
    }
    return testapp.post_json('/experimental_condition', item, status=201).json['@graph'][0]


@pytest.fixture
def experimental_condition_ph(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'condition': 'pH',
        'value': 7.4,
        'units': 'pH units',
        'status': 'current',
    }
    return testapp.post_json('/experimental_condition', item, status=201).json['@graph'][0]


@pytest.fixture
def experimental_condition_diet(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'condition': 'diet',
        'text_value': 'high fat diet',
        'status': 'current',
    }
    return testapp.post_json('/experimental_condition', item, status=201).json['@graph'][0]


@pytest.fixture
def experimental_condition_with_aliases(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'condition': 'oxygen level',
        'value': 5,
        'units': 'percent',
        'aliases': ['lattice:ec-hypoxia-5pct'],
        'status': 'current',
    }
    return testapp.post_json('/experimental_condition', item, status=201).json['@graph'][0]


@pytest.fixture
def experimental_condition_with_description(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'condition': 'temperature',
        'value': 4,
        'units': 'celsius',
        'description': 'Cold storage condition',
        'status': 'current',
    }
    return testapp.post_json('/experimental_condition', item, status=201).json['@graph'][0]
