import pytest


def _post(testapp, item, status=201):
    return testapp.post_json('/experimental_condition', item, status=status)


def _unresolved_term(testapp):
    return testapp.post_json(
        '/controlled_term',
        {'term_id': 'anti-uniprot:Q00000', 'ontology_source': 'UniProt', 'status': 'current'},
        status=201,
    ).json['@graph'][0]


def test_experimental_condition_summary_description_only(testapp, experimental_condition_description_only):
    res = testapp.get(experimental_condition_description_only['@id'])
    assert res.json['summary'] == 'Cold storage condition'


def test_experimental_condition_summary_prefers_description_over_terms(
    testapp, experimental_condition_terms_and_description
):
    res = testapp.get(experimental_condition_terms_and_description['@id'])
    assert res.json['summary'] == 'Insulin stimulation'


def test_experimental_condition_summary_single_term(testapp, experimental_condition_single_term):
    res = testapp.get(experimental_condition_single_term['@id'])
    assert res.json['summary'] == 'INS_HUMAN'


def test_experimental_condition_summary_single_time_point(testapp, experimental_condition_time_point):
    res = testapp.get(experimental_condition_time_point['@id'])
    assert res.json['summary'] == 'INS_HUMAN, 8 hours'


def test_experimental_condition_summary_time_point_range(testapp, experimental_condition_time_point_range):
    res = testapp.get(experimental_condition_time_point_range['@id'])
    assert res.json['summary'] == 'INS_HUMAN, 2-3 hours'


@pytest.mark.parametrize(
    'lower,upper,units,expected',
    [
        (1, 1, 'day', 'INS_HUMAN, 1 day'),
        (0.5, 0.5, 'hour', 'INS_HUMAN, 0.5 hours'),
        (0, 1, 'week', 'INS_HUMAN, 0-1 weeks'),
        (1.5, 2.5, 'minute', 'INS_HUMAN, 1.5-2.5 minutes'),
    ]
)
def test_experimental_condition_summary_time_point_formatting(
    testapp, other_lab, controlled_term_uniprot, lower, upper, units, expected
):
    item = {
        'lab': other_lab['@id'],
        'controlled_terms': [controlled_term_uniprot['@id']],
        'lower_bound_time_point': lower,
        'upper_bound_time_point': upper,
        'time_point_units': units,
        'status': 'current',
    }
    assert _post(testapp, item).json['@graph'][0]['summary'] == expected


def test_experimental_condition_summary_two_terms(testapp, experimental_condition_multiple_terms):
    res = testapp.get(experimental_condition_multiple_terms['@id'])
    assert res.json['summary'] == 'INS_HUMAN and water, 8 hours'


def test_experimental_condition_summary_three_terms_keep_submitted_order(
    testapp, other_lab, controlled_term_uniprot, controlled_term_chebi
):
    unresolved = _unresolved_term(testapp)
    item = {
        'lab': other_lab['@id'],
        'controlled_terms': [unresolved['@id'], controlled_term_chebi['@id'], controlled_term_uniprot['@id']],
        'status': 'current',
    }
    res = _post(testapp, item)
    assert res.json['@graph'][0]['summary'] == 'anti-uniprot:Q00000, water and INS_HUMAN'


def test_experimental_condition_summary_unresolved_term_falls_back_to_term_id(testapp, other_lab):
    unresolved = _unresolved_term(testapp)
    item = {
        'lab': other_lab['@id'],
        'controlled_terms': [unresolved['@id']],
        'status': 'current',
    }
    assert _post(testapp, item).json['@graph'][0]['summary'] == 'anti-uniprot:Q00000'


def test_experimental_condition_embeds_controlled_terms(testapp, experimental_condition_single_term):
    res = testapp.get(experimental_condition_single_term['@id'] + '?frame=embedded')
    [term] = res.json['controlled_terms']
    assert term['term_id'] == 'uniprot:P01308'
    assert term['term_name'] == 'INS_HUMAN'
    assert term['ontology_source'] == 'UniProt'


def test_experimental_condition_requires_lab(testapp):
    _post(testapp, {'description': 'Cold storage condition'}, status=422)


def test_experimental_condition_requires_terms_or_description(testapp, other_lab):
    _post(testapp, {'lab': other_lab['@id'], 'status': 'current'}, status=422)
    _post(
        testapp,
        {
            'lab': other_lab['@id'],
            'lower_bound_time_point': 8,
            'upper_bound_time_point': 8,
            'time_point_units': 'hour',
            'status': 'current',
        },
        status=422,
    )


def test_experimental_condition_rejects_removing_last_of_terms_and_description(
    testapp, experimental_condition_single_term
):
    res = testapp.get(experimental_condition_single_term['@id'] + '@@edit')
    item = {key: value for key, value in res.json.items() if key != 'controlled_terms'}
    testapp.put_json(experimental_condition_single_term['@id'], item, status=422)


def test_experimental_condition_controlled_terms_must_not_be_empty(testapp, other_lab):
    _post(
        testapp,
        {'lab': other_lab['@id'], 'controlled_terms': [], 'description': 'Empty list', 'status': 'current'},
        status=422,
    )


def test_experimental_condition_controlled_terms_must_be_unique(testapp, other_lab, controlled_term_uniprot):
    _post(
        testapp,
        {
            'lab': other_lab['@id'],
            'controlled_terms': [controlled_term_uniprot['@id'], controlled_term_uniprot['@id']],
            'status': 'current',
        },
        status=422,
    )


@pytest.mark.parametrize(
    'time_point',
    [
        {'lower_bound_time_point': 8},
        {'upper_bound_time_point': 8},
        {'time_point_units': 'hour'},
        {'lower_bound_time_point': 8, 'upper_bound_time_point': 8},
        {'lower_bound_time_point': 8, 'time_point_units': 'hour'},
    ]
)
def test_experimental_condition_time_point_properties_required_together(
    testapp, other_lab, controlled_term_uniprot, time_point
):
    item = {
        'lab': other_lab['@id'],
        'controlled_terms': [controlled_term_uniprot['@id']],
        'status': 'current',
        **time_point,
    }
    _post(testapp, item, status=422)


def test_experimental_condition_upper_time_point_below_lower_rejected(testapp, other_lab, controlled_term_uniprot):
    res = _post(
        testapp,
        {
            'lab': other_lab['@id'],
            'controlled_terms': [controlled_term_uniprot['@id']],
            'lower_bound_time_point': 24,
            'upper_bound_time_point': 12,
            'time_point_units': 'hour',
            'status': 'current',
        },
        status=422,
    )
    assert 'upper_bound_time_point must be greater than or equal to lower_bound_time_point.' in res.text


def test_experimental_condition_negative_time_point_rejected(testapp, other_lab, controlled_term_uniprot):
    _post(
        testapp,
        {
            'lab': other_lab['@id'],
            'controlled_terms': [controlled_term_uniprot['@id']],
            'lower_bound_time_point': -1,
            'upper_bound_time_point': 2,
            'time_point_units': 'hour',
            'status': 'current',
        },
        status=422,
    )


def test_experimental_condition_time_point_units_enum(testapp, other_lab, controlled_term_uniprot):
    _post(
        testapp,
        {
            'lab': other_lab['@id'],
            'controlled_terms': [controlled_term_uniprot['@id']],
            'lower_bound_time_point': 8,
            'upper_bound_time_point': 8,
            'time_point_units': 'hours',
            'status': 'current',
        },
        status=422,
    )


def test_experimental_condition_create_with_all_fields(testapp, other_lab, controlled_term_uniprot):
    item = {
        'lab': other_lab['@id'],
        'controlled_terms': [controlled_term_uniprot['@id']],
        'description': 'Insulin stimulation',
        'lower_bound_time_point': 2,
        'upper_bound_time_point': 3,
        'time_point_units': 'day',
        'aliases': ['lattice:ec-test-complete'],
        'status': 'current',
    }
    row = _post(testapp, item).json['@graph'][0]
    assert row['controlled_terms'] == [controlled_term_uniprot['@id']]
    assert row['description'] == 'Insulin stimulation'
    assert row['lower_bound_time_point'] == 2
    assert row['upper_bound_time_point'] == 3
    assert row['time_point_units'] == 'day'
    assert row['aliases'] == ['lattice:ec-test-complete']


@pytest.mark.parametrize(
    'legacy',
    [
        {'condition': 'temperature'},
        {'value': 37},
        {'units': 'celsius'},
        {'text_value': 'fasting'},
        {'lower_bound_duration': 8, 'upper_bound_duration': 8, 'duration_units': 'hour'},
    ]
)
def test_experimental_condition_rejects_legacy_properties(testapp, other_lab, legacy):
    _post(
        testapp,
        {'lab': other_lab['@id'], 'description': 'Legacy shape', 'status': 'current', **legacy},
        status=422,
    )


def test_experimental_condition_rejects_legacy_controlled_term(testapp, other_lab, controlled_term_uniprot):
    _post(
        testapp,
        {'lab': other_lab['@id'], 'controlled_term': controlled_term_uniprot['@id'], 'status': 'current'},
        status=422,
    )
