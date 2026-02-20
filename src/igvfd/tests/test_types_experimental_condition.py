import pytest


def test_experimental_condition_summary_with_aliases(testapp, experimental_condition_with_aliases):
    res = testapp.get(experimental_condition_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:ec-hypoxia-5pct'


def test_experimental_condition_summary_with_description(testapp, experimental_condition_with_description):
    res = testapp.get(experimental_condition_with_description['@id'])
    assert res.json.get('summary') == 'Cold storage condition'


def test_experimental_condition_summary_quantitative(testapp, experimental_condition_temperature):
    res = testapp.get(experimental_condition_temperature['@id'])
    assert res.json.get('summary') == 'temperature 37 celsius'


def test_experimental_condition_summary_qualitative(testapp, experimental_condition_diet):
    res = testapp.get(experimental_condition_diet['@id'])
    assert res.json.get('summary') == 'diet: high fat diet'


def test_experimental_condition_required_fields(testapp, other_lab):
    testapp.post_json(
        '/experimental_condition',
        {
            'lab': other_lab['@id'],
        },
        status=422
    )
    testapp.post_json(
        '/experimental_condition',
        {
            'condition': 'temperature',
            'value': 37,
            'units': 'celsius',
        },
        status=422
    )


def test_experimental_condition_condition_enum_invalid(testapp, other_lab):
    testapp.post_json(
        '/experimental_condition',
        {
            'lab': other_lab['@id'],
            'condition': 'invalid_condition',
        },
        status=422
    )


def test_experimental_condition_quantitative_requires_value_and_units(testapp, other_lab):
    testapp.post_json(
        '/experimental_condition',
        {
            'lab': other_lab['@id'],
            'condition': 'temperature',
        },
        status=422
    )
    testapp.post_json(
        '/experimental_condition',
        {
            'lab': other_lab['@id'],
            'condition': 'temperature',
            'value': 37,
        },
        status=422
    )
    testapp.post_json(
        '/experimental_condition',
        {
            'lab': other_lab['@id'],
            'condition': 'temperature',
            'units': 'celsius',
        },
        status=422
    )


def test_experimental_condition_qualitative_requires_text_value(testapp, other_lab):
    testapp.post_json(
        '/experimental_condition',
        {
            'lab': other_lab['@id'],
            'condition': 'diet',
        },
        status=422
    )
    testapp.post_json(
        '/experimental_condition',
        {
            'lab': other_lab['@id'],
            'condition': 'smoking status',
        },
        status=422
    )


def test_experimental_condition_value_units_mutual_dependency(testapp, other_lab):
    testapp.post_json(
        '/experimental_condition',
        {
            'lab': other_lab['@id'],
            'condition': 'diet',
            'text_value': 'normal chow',
            'value': 10,
        },
        status=422
    )
    testapp.post_json(
        '/experimental_condition',
        {
            'lab': other_lab['@id'],
            'condition': 'diet',
            'text_value': 'normal chow',
            'units': 'celsius',
        },
        status=422
    )


@pytest.mark.parametrize(
    'condition,value,units',
    [
        ('temperature', 37, 'celsius'),
        ('temperature', 98.6, 'fahrenheit'),
        ('temperature', 310.15, 'kelvin'),
        ('pH', 7.4, 'pH units'),
        ('oxygen level', 21, 'percent'),
        ('humidity', 95, 'percent'),
        ('pressure', 101.325, 'kPa'),
        ('pressure', 760, 'mmHg'),
        ('surface tension', 72, 'mN/m'),
        ('surface tension', 72, 'dyn/cm'),
        ('osmolarity', 300, 'mOsm/kg'),
    ]
)
def test_experimental_condition_create_quantitative(testapp, other_lab, condition, value, units):
    item = {
        'lab': other_lab['@id'],
        'condition': condition,
        'value': value,
        'units': units,
        'status': 'current',
    }
    res = testapp.post_json('/experimental_condition', item, status=201)
    assert res.json['@graph'][0]['condition'] == condition
    assert res.json['@graph'][0]['value'] == value
    assert res.json['@graph'][0]['units'] == units


@pytest.mark.parametrize(
    'condition,text_value',
    [
        ('diet', 'high fat diet'),
        ('diet', 'normal chow'),
        ('smoking status', 'current smoker'),
        ('smoking status', 'non-smoker'),
    ]
)
def test_experimental_condition_create_qualitative(testapp, other_lab, condition, text_value):
    item = {
        'lab': other_lab['@id'],
        'condition': condition,
        'text_value': text_value,
        'status': 'current',
    }
    res = testapp.post_json('/experimental_condition', item, status=201)
    assert res.json['@graph'][0]['condition'] == condition
    assert res.json['@graph'][0]['text_value'] == text_value


def test_experimental_condition_create_with_all_fields(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'condition': 'temperature',
        'value': 4,
        'units': 'celsius',
        'description': 'Cold storage for sample preservation.',
        'aliases': ['lattice:ec-test-complete'],
        'status': 'current',
    }
    res = testapp.post_json('/experimental_condition', item, status=201)
    assert res.json['@graph'][0]['condition'] == 'temperature'
    assert res.json['@graph'][0]['value'] == 4
    assert res.json['@graph'][0]['units'] == 'celsius'
    assert res.json['@graph'][0]['description'] == 'Cold storage for sample preservation.'
    assert res.json['@graph'][0]['aliases'] == ['lattice:ec-test-complete']
