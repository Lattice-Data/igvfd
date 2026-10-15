import pytest


@pytest.fixture
def experimental_condition_description_only(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'description': 'Cold storage condition',
        'status': 'current',
    }
    return testapp.post_json('/experimental_condition', item, status=201).json['@graph'][0]


@pytest.fixture
def experimental_condition_single_term(testapp, other_lab, controlled_term_uniprot):
    item = {
        'lab': other_lab['@id'],
        'controlled_terms': [controlled_term_uniprot['@id']],
        'status': 'current',
    }
    return testapp.post_json('/experimental_condition', item, status=201).json['@graph'][0]


@pytest.fixture
def experimental_condition_time_point(testapp, other_lab, controlled_term_uniprot):
    item = {
        'lab': other_lab['@id'],
        'controlled_terms': [controlled_term_uniprot['@id']],
        'lower_bound_time_point': 8,
        'upper_bound_time_point': 8,
        'time_point_units': 'hour',
        'status': 'current',
    }
    return testapp.post_json('/experimental_condition', item, status=201).json['@graph'][0]


@pytest.fixture
def experimental_condition_time_point_range(testapp, other_lab, controlled_term_uniprot):
    item = {
        'lab': other_lab['@id'],
        'controlled_terms': [controlled_term_uniprot['@id']],
        'lower_bound_time_point': 2,
        'upper_bound_time_point': 3,
        'time_point_units': 'hour',
        'status': 'current',
    }
    return testapp.post_json('/experimental_condition', item, status=201).json['@graph'][0]


@pytest.fixture
def experimental_condition_multiple_terms(testapp, other_lab, controlled_term_uniprot, controlled_term_chebi):
    item = {
        'lab': other_lab['@id'],
        'controlled_terms': [controlled_term_uniprot['@id'], controlled_term_chebi['@id']],
        'lower_bound_time_point': 8,
        'upper_bound_time_point': 8,
        'time_point_units': 'hour',
        'status': 'current',
    }
    return testapp.post_json('/experimental_condition', item, status=201).json['@graph'][0]


@pytest.fixture
def experimental_condition_terms_and_description(testapp, other_lab, controlled_term_uniprot):
    item = {
        'lab': other_lab['@id'],
        'controlled_terms': [controlled_term_uniprot['@id']],
        'description': 'Insulin stimulation',
        'lower_bound_time_point': 8,
        'upper_bound_time_point': 8,
        'time_point_units': 'hour',
        'status': 'current',
    }
    return testapp.post_json('/experimental_condition', item, status=201).json['@graph'][0]
