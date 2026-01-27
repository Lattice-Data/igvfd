import pytest


def test_primary_cell_culture_summary_with_aliases(testapp, primary_cell_culture_with_aliases):
    res = testapp.get(primary_cell_culture_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:primary-cell-passage-3'


def test_primary_cell_culture_summary_with_description(testapp, primary_cell_culture_with_description):
    res = testapp.get(primary_cell_culture_with_description['@id'])
    assert res.json.get('summary') == 'Test primary cell culture sample'


def test_primary_cell_culture_summary_with_uuid(testapp, primary_cell_culture):
    res = testapp.get(primary_cell_culture['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


def test_primary_cell_culture_required_fields(testapp, other_lab, human_donor, controlled_term_brain):
    # Missing lab
    testapp.post_json(
        '/primary_cell_culture',
        {
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
        },
        status=422
    )
    # Missing donors
    testapp.post_json(
        '/primary_cell_culture',
        {
            'lab': other_lab['@id'],
            'sample_terms': [controlled_term_brain['@id']],
        },
        status=422
    )
    # Missing sample_terms
    testapp.post_json(
        '/primary_cell_culture',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
        },
        status=422
    )


def test_primary_cell_culture_passage_number_minimum(testapp, other_lab, human_donor, controlled_term_brain):
    testapp.post_json(
        '/primary_cell_culture',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'passage_number': -1,
            'status': 'current',
        },
        status=422
    )


def test_primary_cell_culture_date_obtained_format(testapp, other_lab, human_donor, controlled_term_brain):
    # Invalid date format
    testapp.post_json(
        '/primary_cell_culture',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'date_obtained': 'invalid-date',
            'status': 'current',
        },
        status=422
    )


def test_primary_cell_culture_create_success(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/primary_cell_culture', item, status=201)
    assert res.json['@graph'][0]['lab'] == other_lab['@id']
    assert res.json['@graph'][0]['donors'] == [human_donor['@id']]
    assert res.json['@graph'][0]['sample_terms'] == [controlled_term_brain['@id']]


def test_primary_cell_culture_create_with_passage_number(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'passage_number': 5,
        'status': 'current',
    }
    res = testapp.post_json('/primary_cell_culture', item, status=201)
    assert res.json['@graph'][0]['passage_number'] == 5


def test_primary_cell_culture_create_with_all_optional_fields(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'passage_number': 3,
        'date_obtained': '2024-02-20',
        'description': 'Human primary cell culture',
        'status': 'current',
    }
    res = testapp.post_json('/primary_cell_culture', item, status=201)
    assert res.json['@graph'][0]['passage_number'] == 3
    assert res.json['@graph'][0]['date_obtained'] == '2024-02-20'
    assert res.json['@graph'][0]['description'] == 'Human primary cell culture'


def test_primary_cell_culture_passage_number_zero(testapp, other_lab, human_donor, controlled_term_brain):
    # passage_number = 0 should be valid (minimum is 0)
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'passage_number': 0,
        'status': 'current',
    }
    res = testapp.post_json('/primary_cell_culture', item, status=201)
    assert res.json['@graph'][0]['passage_number'] == 0
