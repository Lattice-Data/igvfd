import pytest


def test_tissue_preservation_method_enum(testapp, other_lab, human_donor, controlled_term_brain):
    testapp.post_json(
        '/tissue',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'preservation_method': 'invalid_method',
            'status': 'current',
        },
        status=422
    )


def test_tissue_orientation_enum(testapp, other_lab, human_donor, controlled_term_brain):
    testapp.post_json(
        '/tissue',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'orientation': 'invalid_orientation',
            'status': 'current',
        },
        status=422
    )


def test_tissue_thickness_units_enum(testapp, other_lab, human_donor, controlled_term_brain):
    testapp.post_json(
        '/tissue',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'thickness': 5.0,
            'thickness_units': 'invalid_unit',
            'status': 'current',
        },
        status=422
    )


def test_tissue_thickness_dependency(testapp, other_lab, human_donor, controlled_term_brain):
    # thickness without thickness_units should fail
    testapp.post_json(
        '/tissue',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'thickness': 5.0,
            'status': 'current',
        },
        status=422
    )
    # thickness_units without thickness should fail
    testapp.post_json(
        '/tissue',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'thickness_units': 'mm',
            'status': 'current',
        },
        status=422
    )


def test_tissue_thickness_minimum(testapp, other_lab, human_donor, controlled_term_brain):
    testapp.post_json(
        '/tissue',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'thickness': -1,
            'thickness_units': 'mm',
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize(
    'preservation_method',
    [
        'fresh',
        'frozen',
        'flash-frozen',
        'fixed',
        'fixed-frozen',
        'cryopreserved',
        'paraffin embedded',
        'OCT embedded'
    ]
)
def test_tissue_create_with_preservation_method_enum_values(testapp, other_lab, human_donor, controlled_term_brain, preservation_method):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'preservation_method': preservation_method,
        'status': 'current',
    }
    res = testapp.post_json('/tissue', item, status=201)
    assert res.json['@graph'][0]['preservation_method'] == preservation_method


@pytest.mark.parametrize(
    'orientation',
    [
        'coronal',
        'lateral',
        'longitudinal',
        'sagittal',
        'transverse'
    ]
)
def test_tissue_create_with_orientation_enum_values(testapp, other_lab, human_donor, controlled_term_brain, orientation):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'orientation': orientation,
        'status': 'current',
    }
    res = testapp.post_json('/tissue', item, status=201)
    assert res.json['@graph'][0]['orientation'] == orientation


def test_tissue_create_success(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/tissue', item, status=201)
    assert res.json['@graph'][0]['lab'] == other_lab['@id']
    assert res.json['@graph'][0]['donors'] == [human_donor['@id']]
    assert res.json['@graph'][0]['sample_terms'] == [controlled_term_brain['@id']]


def test_tissue_create_with_all_optional_fields(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'spatial_information': 'Frontal lobe, left hemisphere',
        'preservation_method': 'frozen',
        'thickness': 5.0,
        'thickness_units': 'mm',
        'date_obtained': '2024-01-15',
        'orientation': 'coronal',
        'lower_bound_age': 30,
        'upper_bound_age': 45,
        'age_units': 'year',
        'status': 'current',
    }
    res = testapp.post_json('/tissue', item, status=201)
    assert res.json['@graph'][0]['spatial_information'] == 'Frontal lobe, left hemisphere'
    assert res.json['@graph'][0]['preservation_method'] == 'frozen'
    assert res.json['@graph'][0]['thickness'] == 5.0
    assert res.json['@graph'][0]['thickness_units'] == 'mm'
    assert res.json['@graph'][0]['date_obtained'] == '2024-01-15'
    assert res.json['@graph'][0]['orientation'] == 'coronal'
    assert res.json['@graph'][0]['lower_bound_age'] == 30
    assert res.json['@graph'][0]['upper_bound_age'] == 45
    assert res.json['@graph'][0]['age_units'] == 'year'


def test_tissue_age_dependency(testapp, other_lab, human_donor, controlled_term_brain):
    testapp.post_json(
        '/tissue',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'lower_bound_age': 40,
            'status': 'current',
        },
        status=422
    )
    testapp.post_json(
        '/tissue',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'age_units': 'year',
            'status': 'current',
        },
        status=422
    )


def test_tissue_age_units_enum(testapp, other_lab, human_donor, controlled_term_brain):
    testapp.post_json(
        '/tissue',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'lower_bound_age': 1,
            'upper_bound_age': 2,
            'age_units': 'fortnight',
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize(
    'age_units',
    [
        'minute',
        'hour',
        'day',
        'week',
        'month',
        'year',
    ]
)
def test_tissue_create_with_age_units_enum_values(testapp, other_lab, human_donor, controlled_term_brain, age_units):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'lower_bound_age': 10,
        'upper_bound_age': 10,
        'age_units': age_units,
        'status': 'current',
    }
    res = testapp.post_json('/tissue', item, status=201)
    assert res.json['@graph'][0]['age_units'] == age_units


def test_tissue_create_with_age_range(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'lower_bound_age': 18,
        'upper_bound_age': 25,
        'age_units': 'year',
        'status': 'current',
    }
    res = testapp.post_json('/tissue', item, status=201)
    assert res.json['@graph'][0]['lower_bound_age'] == 18
    assert res.json['@graph'][0]['upper_bound_age'] == 25


def test_tissue_create_with_age_point_estimate(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'lower_bound_age': 33,
        'upper_bound_age': 33,
        'age_units': 'year',
        'status': 'current',
    }
    res = testapp.post_json('/tissue', item, status=201)
    assert res.json['@graph'][0]['lower_bound_age'] == 33
    assert res.json['@graph'][0]['upper_bound_age'] == 33


def test_tissue_age_minimum(testapp, other_lab, human_donor, controlled_term_brain):
    testapp.post_json(
        '/tissue',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'lower_bound_age': -1,
            'upper_bound_age': 1,
            'age_units': 'year',
            'status': 'current',
        },
        status=422
    )
