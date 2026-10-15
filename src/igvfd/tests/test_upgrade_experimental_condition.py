def _upgrade(upgrader, value):
    return upgrader.upgrade('experimental_condition', value, current_version='2', target_version='3')


def test_experimental_condition_upgrade_2_3_protein_treatment(upgrader):
    value = {
        'schema_version': '2',
        'lab': 'alex-marson',
        'condition': 'protein treatment',
        'controlled_term': '/controlled-terms/anti-uniprot:P07766/',
        'lower_bound_duration': 8,
        'upper_bound_duration': 8,
        'duration_units': 'hour',
        'description': 'stimulation',
        'status': 'current',
    }
    result = _upgrade(upgrader, value)
    assert result['schema_version'] == '3'
    assert result['controlled_terms'] == ['/controlled-terms/anti-uniprot:P07766/']
    assert result['lower_bound_time_point'] == 8
    assert result['upper_bound_time_point'] == 8
    assert result['time_point_units'] == 'hour'
    assert result['description'] == 'stimulation'
    assert result['notes'] == 'Legacy properties removed during schema upgrade: condition=protein treatment.'
    for removed in (
        'condition', 'controlled_term', 'value', 'units', 'text_value',
        'lower_bound_duration', 'upper_bound_duration', 'duration_units',
    ):
        assert removed not in result


def test_experimental_condition_upgrade_2_3_text_value_becomes_description(upgrader):
    value = {
        'schema_version': '2',
        'condition': 'diet',
        'controlled_term': '/controlled-terms/EFO:0002755/',
        'text_value': 'fasting',
        'lower_bound_duration': 20,
        'upper_bound_duration': 20,
        'duration_units': 'hour',
    }
    result = _upgrade(upgrader, value)
    assert result['controlled_terms'] == ['/controlled-terms/EFO:0002755/']
    assert result['description'] == 'fasting'
    assert result['notes'] == 'Legacy properties removed during schema upgrade: condition=diet.'


def test_experimental_condition_upgrade_2_3_text_value_kept_in_notes_when_description_exists(upgrader):
    value = {
        'schema_version': '2',
        'condition': 'chemical treatment',
        'text_value': 'ethanol',
        'value': 3,
        'units': 'percent',
        'description': 'Ethanol exposure',
        'notes': 'Existing note.',
    }
    result = _upgrade(upgrader, value)
    assert result['description'] == 'Ethanol exposure'
    assert result['notes'] == (
        'Existing note.\n'
        'Legacy properties removed during schema upgrade: '
        'condition=chemical treatment, value=3, units=percent, text_value=ethanol.'
    )
    assert 'controlled_terms' not in result


def test_experimental_condition_upgrade_2_3_duration_range(upgrader):
    value = {
        'schema_version': '2',
        'condition': 'diet',
        'text_value': 'high fat diet',
        'lower_bound_duration': 7,
        'upper_bound_duration': 14,
        'duration_units': 'day',
    }
    result = _upgrade(upgrader, value)
    assert result['lower_bound_time_point'] == 7
    assert result['upper_bound_time_point'] == 14
    assert result['time_point_units'] == 'day'


def test_experimental_condition_upgrade_2_3_quantitative_condition_gets_description(upgrader):
    value = {
        'schema_version': '2',
        'condition': 'temperature',
        'value': 37.0,
        'units': 'celsius',
    }
    result = _upgrade(upgrader, value)
    assert result['description'] == 'temperature 37 celsius'
    assert result['notes'] == (
        'Legacy properties removed during schema upgrade: condition=temperature, value=37, units=celsius.'
    )


def test_experimental_condition_upgrade_2_3_keeps_description_of_quantitative_condition(upgrader):
    value = {
        'schema_version': '2',
        'condition': 'pH',
        'value': 7.4,
        'units': 'pH units',
        'description': 'Physiological pH.',
    }
    result = _upgrade(upgrader, value)
    assert result['description'] == 'Physiological pH.'
    assert result['notes'] == (
        'Legacy properties removed during schema upgrade: condition=pH, value=7.4, units=pH units.'
    )


def test_experimental_condition_upgrade_1_3(upgrader):
    value = {
        'schema_version': '1',
        'condition': 'smoking status',
        'text_value': 'current smoker',
        'aliases': ['lattice:kept alias', 'lattice:dropped-alias\n'],
    }
    result = upgrader.upgrade('experimental_condition', value, current_version='1', target_version='3')
    assert result['schema_version'] == '3'
    assert result['aliases'] == ['lattice:kept alias']
    assert result['description'] == 'current smoker'
    assert result['notes'] == (
        'Aliases removed during schema upgrade: "lattice:dropped-alias\\n".\n'
        'Legacy properties removed during schema upgrade: condition=smoking status.'
    )
