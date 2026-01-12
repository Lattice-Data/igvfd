import pytest


def test_genetic_modification_summary_with_description(testapp, genetic_modification_with_description):
    res = testapp.get(genetic_modification_with_description['@id'])
    assert res.json.get('summary') == 'CRISPRi-based gene silencing modification.'


def test_genetic_modification_summary_with_modality(testapp, genetic_modification):
    res = testapp.get(genetic_modification['@id'])
    # When description is missing, summary should use modality
    assert res.json.get('summary') == 'knockout'


def test_genetic_modification_summary_with_aliases(testapp, genetic_modification_with_aliases):
    res = testapp.get(genetic_modification_with_aliases['@id'])
    # Summary prioritizes modality over aliases when description is missing
    assert res.json.get('summary') == 'cutting'


def test_genetic_modification_required_fields(testapp):
    # Test that modality is required
    testapp.post_json(
        '/genetic_modification',
        {
            'description': 'A modification without modality.',
        },
        status=422
    )


def test_genetic_modification_modality_enum(testapp):
    # Test that only valid modality values are allowed
    testapp.post_json(
        '/genetic_modification',
        {
            'modality': 'invalid_modality',
        },
        status=422
    )


def test_genetic_modification_create(testapp):
    item = {
        'modality': 'knockout',
        'status': 'current',
    }
    res = testapp.post_json('/genetic_modification', item, status=201)
    assert res.json['@graph'][0]['modality'] == 'knockout'


def test_genetic_modification_create_with_all_fields(testapp):
    item = {
        'modality': 'prime editing',
        'description': 'Prime editing for precise insertions.',
        'aliases': ['lattice:gm-test-complete'],
        'status': 'current',
    }
    res = testapp.post_json('/genetic_modification', item, status=201)
    assert res.json['@graph'][0]['modality'] == 'prime editing'
    assert res.json['@graph'][0]['description'] == 'Prime editing for precise insertions.'
    assert res.json['@graph'][0]['aliases'] == ['lattice:gm-test-complete']


def test_genetic_modification_all_modalities(testapp):
    # Test all valid modality values
    modalities = [
        'activation',
        'base editing',
        'cutting',
        'interference',
        'knockout',
        'localizing',
        'prime editing',
    ]
    for modality in modalities:
        item = {
            'modality': modality,
            'status': 'current',
        }
        res = testapp.post_json('/genetic_modification', item, status=201)
        assert res.json['@graph'][0]['modality'] == modality
