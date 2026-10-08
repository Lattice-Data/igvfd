import pytest


def test_experimental_condition_summary_ignores_aliases(testapp, experimental_condition_with_aliases):
    res = testapp.get(experimental_condition_with_aliases['@id'])
    assert res.json.get('summary') == 'Oxygen level 5%'


def test_experimental_condition_summary_ignores_description(testapp, experimental_condition_with_description):
    res = testapp.get(experimental_condition_with_description['@id'])
    assert res.json.get('summary') == 'Temperature 4 celsius'


def test_experimental_condition_summary_quantitative(testapp, experimental_condition_temperature):
    res = testapp.get(experimental_condition_temperature['@id'])
    assert res.json.get('summary') == 'Temperature 37 celsius'


def test_experimental_condition_summary_ph(testapp, experimental_condition_ph):
    res = testapp.get(experimental_condition_ph['@id'])
    assert res.json.get('summary') == 'pH 7.4'


def test_experimental_condition_summary_qualitative(testapp, experimental_condition_diet):
    res = testapp.get(experimental_condition_diet['@id'])
    assert res.json.get('summary') == 'Diet: high fat diet'


def test_experimental_condition_summary_duration_range(testapp, experimental_condition_with_duration):
    res = testapp.get(experimental_condition_with_duration['@id'])
    assert res.json.get('summary') == 'Temperature 37 celsius for 12 to 24 hours'


def test_experimental_condition_summary_chemical_treatment_text_agent(
    testapp, experimental_condition_chemical_treatment_ethanol
):
    res = testapp.get(experimental_condition_chemical_treatment_ethanol['@id'])
    assert res.json.get('summary') == 'Chemical treatment with ethanol at 3% for 4 hours'


def test_experimental_condition_summary_protein_treatment_term_agent(
    testapp, experimental_condition_protein_treatment, controlled_term_uniprot
):
    res = testapp.get(experimental_condition_protein_treatment['@id'])
    term = testapp.get(controlled_term_uniprot['@id']).json
    agent = term.get('term_name') or term['term_id']
    assert res.json.get('summary') == f'Protein treatment with {agent} at 10 ng/mL for 1 day'


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


def test_experimental_condition_controlled_term_optional(
    testapp, other_lab, controlled_term_efo
):
    item = {
        'lab': other_lab['@id'],
        'condition': 'diet',
        'text_value': 'high fat diet',
        'status': 'current',
    }
    res = testapp.post_json('/experimental_condition', item, status=201)
    assert 'controlled_term' not in res.json['@graph'][0]


def test_experimental_condition_create_with_controlled_term(
    testapp, other_lab, controlled_term_efo
):
    item = {
        'lab': other_lab['@id'],
        'condition': 'diet',
        'text_value': 'high fat diet',
        'controlled_term': controlled_term_efo['@id'],
        'status': 'current',
    }
    res = testapp.post_json('/experimental_condition', item, status=201)
    assert res.json['@graph'][0]['controlled_term'] == controlled_term_efo['@id']


def test_experimental_condition_duration_dependency(testapp, other_lab):
    testapp.post_json(
        '/experimental_condition',
        {
            'lab': other_lab['@id'],
            'condition': 'temperature',
            'value': 37,
            'units': 'celsius',
            'lower_bound_duration': 12,
            'status': 'current',
        },
        status=422
    )
    testapp.post_json(
        '/experimental_condition',
        {
            'lab': other_lab['@id'],
            'condition': 'temperature',
            'value': 37,
            'units': 'celsius',
            'duration_units': 'hour',
            'status': 'current',
        },
        status=422
    )


def test_experimental_condition_create_with_duration_range(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'condition': 'temperature',
        'value': 37,
        'units': 'celsius',
        'lower_bound_duration': 12,
        'upper_bound_duration': 24,
        'duration_units': 'hour',
        'status': 'current',
    }
    res = testapp.post_json('/experimental_condition', item, status=201)
    assert res.json['@graph'][0]['lower_bound_duration'] == 12
    assert res.json['@graph'][0]['upper_bound_duration'] == 24
    assert res.json['@graph'][0]['duration_units'] == 'hour'


def test_experimental_condition_upper_duration_below_lower_rejected(testapp, other_lab):
    testapp.post_json(
        '/experimental_condition',
        {
            'lab': other_lab['@id'],
            'condition': 'temperature',
            'value': 37,
            'units': 'celsius',
            'lower_bound_duration': 24,
            'upper_bound_duration': 12,
            'duration_units': 'hour',
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize('condition', ['chemical treatment', 'protein treatment'])
def test_experimental_condition_treatment_requires_agent(testapp, other_lab, condition):
    testapp.post_json(
        '/experimental_condition',
        {
            'lab': other_lab['@id'],
            'condition': condition,
            'status': 'current',
        },
        status=422
    )


def test_experimental_condition_treatment_with_controlled_term(testapp, other_lab, controlled_term_chebi):
    item = {
        'lab': other_lab['@id'],
        'condition': 'chemical treatment',
        'controlled_term': controlled_term_chebi['@id'],
        'status': 'current',
    }
    res = testapp.post_json('/experimental_condition', item, status=201)
    assert res.json['@graph'][0]['controlled_term'] == controlled_term_chebi['@id']


def test_experimental_condition_treatment_with_text_value(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'condition': 'chemical treatment',
        'text_value': 'ethanol',
        'status': 'current',
    }
    res = testapp.post_json('/experimental_condition', item, status=201)
    assert res.json['@graph'][0]['text_value'] == 'ethanol'


@pytest.mark.parametrize(
    'units',
    ['mg/kg', 'mg/mL', 'mM', 'ng/mL', 'nM', 'percent', 'μg/kg', 'μg/mL', 'μM', 'kPa'],
)
def test_experimental_condition_treatment_amount_units_accepted(testapp, other_lab, units):
    item = {
        'lab': other_lab['@id'],
        'condition': 'chemical treatment',
        'text_value': 'ethanol',
        'value': 3,
        'units': units,
        'status': 'current',
    }
    testapp.post_json('/experimental_condition', item, status=201)


@pytest.mark.parametrize('units', ['celsius', 'pH units', 'mmHg'])
def test_experimental_condition_treatment_rejects_condition_units(testapp, other_lab, units):
    testapp.post_json(
        '/experimental_condition',
        {
            'lab': other_lab['@id'],
            'condition': 'chemical treatment',
            'text_value': 'ethanol',
            'value': 3,
            'units': units,
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize('units', ['mg/kg', 'mM', 'ng/mL', 'μM'])
def test_experimental_condition_non_treatment_rejects_amount_units(testapp, other_lab, units):
    testapp.post_json(
        '/experimental_condition',
        {
            'lab': other_lab['@id'],
            'condition': 'temperature',
            'value': 5,
            'units': units,
            'status': 'current',
        },
        status=422
    )
