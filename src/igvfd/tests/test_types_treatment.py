import pytest


def test_treatment_summary_with_aliases(testapp, treatment_with_aliases):
    res = testapp.get(treatment_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:treatment-water'


def test_treatment_summary_with_description(testapp, treatment_with_description):
    res = testapp.get(treatment_with_description['@id'])
    assert res.json.get('summary') == 'Water vehicle control treatment'


def test_treatment_summary_fallback_to_uuid(testapp, treatment):
    res = testapp.get(treatment['@id'])
    assert res.json.get('summary') == treatment['uuid']


def test_treatment_required_fields(testapp, other_lab, controlled_term_chebi):
    testapp.post_json(
        '/treatment',
        {
            'lab': other_lab['@id'],
        },
        status=422
    )
    testapp.post_json(
        '/treatment',
        {
            'ontological_term': controlled_term_chebi['@id'],
        },
        status=422
    )


def test_treatment_create_success(testapp, other_lab, controlled_term_chebi):
    item = {
        'lab': other_lab['@id'],
        'ontological_term': controlled_term_chebi['@id'],
        'status': 'current',
    }
    res = testapp.post_json('/treatment', item, status=201)
    assert res.json['@graph'][0]['ontological_term'] == controlled_term_chebi['@id']
    assert res.json['@graph'][0]['lab'] == other_lab['@id']


def test_treatment_create_with_all_fields(testapp, other_lab, controlled_term_chebi):
    item = {
        'lab': other_lab['@id'],
        'ontological_term': controlled_term_chebi['@id'],
        'aliases': ['lattice:treatment-full'],
        'description': 'Full treatment example',
        'status': 'current',
    }
    res = testapp.post_json('/treatment', item, status=201)
    assert res.json['@graph'][0]['summary'] == 'lattice:treatment-full'
