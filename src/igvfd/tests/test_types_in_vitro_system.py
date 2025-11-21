import pytest


def test_in_vitro_system_summary_with_aliases(testapp, in_vitro_system_with_aliases):
    res = testapp.get(in_vitro_system_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:in-vitro-organoid'


def test_in_vitro_system_summary_with_description(testapp, in_vitro_system_with_description):
    res = testapp.get(in_vitro_system_with_description['@id'])
    assert res.json.get('summary') == 'Test in vitro system sample'


def test_in_vitro_system_summary_with_uuid(testapp, in_vitro_system):
    res = testapp.get(in_vitro_system['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


def test_in_vitro_system_required_fields(testapp, other_lab, human_donor, controlled_term_brain):
    # Missing lab
    testapp.post_json(
        '/in_vitro_system',
        {
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'classification': 'organoid',
        },
        status=422
    )
    # Missing donors
    testapp.post_json(
        '/in_vitro_system',
        {
            'lab': other_lab['@id'],
            'sample_terms': [controlled_term_brain['@id']],
            'classification': 'organoid',
        },
        status=422
    )
    # Missing sample_terms
    testapp.post_json(
        '/in_vitro_system',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'classification': 'organoid',
        },
        status=422
    )
    # Missing classification
    testapp.post_json(
        '/in_vitro_system',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
        },
        status=422
    )


def test_in_vitro_system_classification_enum(testapp, other_lab, human_donor, controlled_term_brain):
    testapp.post_json(
        '/in_vitro_system',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'classification': 'invalid_classification',
            'status': 'current',
        },
        status=422
    )


def test_in_vitro_system_create_success(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'classification': 'organoid',
        'status': 'current',
    }
    res = testapp.post_json('/in_vitro_system', item, status=201)
    assert res.json['@graph'][0]['lab'] == other_lab['@id']
    assert res.json['@graph'][0]['donors'] == [human_donor['@id']]
    assert res.json['@graph'][0]['sample_terms'] == [controlled_term_brain['@id']]
    assert res.json['@graph'][0]['classification'] == 'organoid'


def test_in_vitro_system_create_with_all_optional_fields(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'classification': 'organoid',
        'description': 'Test in vitro system with all fields',
        'status': 'current',
    }
    res = testapp.post_json('/in_vitro_system', item, status=201)
    assert res.json['@graph'][0]['classification'] == 'organoid'
    assert res.json['@graph'][0]['description'] == 'Test in vitro system with all fields'


@pytest.mark.parametrize(
    'classification',
    [
        'organoid',
        'gastruloid',
        'embryoid',
        'immortalized cell line'
    ]
)
def test_in_vitro_system_create_with_classification_enum_values(testapp, other_lab, human_donor, controlled_term_brain, classification):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'classification': classification,
        'status': 'current',
    }
    res = testapp.post_json('/in_vitro_system', item, status=201)
    assert res.json['@graph'][0]['classification'] == classification
