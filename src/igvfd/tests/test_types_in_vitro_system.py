import pytest


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
