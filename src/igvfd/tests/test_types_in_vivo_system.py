import pytest


def test_in_vivo_system_summary_with_aliases(testapp, in_vivo_system_with_aliases):
    res = testapp.get(in_vivo_system_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:in-vivo-xenograft'


def test_in_vivo_system_summary_with_description(testapp, in_vivo_system_with_description):
    res = testapp.get(in_vivo_system_with_description['@id'])
    assert res.json.get('summary') == 'Test in vivo system sample'


def test_in_vivo_system_summary_with_uuid(testapp, in_vivo_system):
    res = testapp.get(in_vivo_system['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


def test_in_vivo_system_required_fields(testapp, other_lab, human_donor, controlled_term_brain):
    # Missing lab
    testapp.post_json(
        '/in_vivo_system',
        {
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'classification': 'xenograft',
        },
        status=422
    )
    # Missing donors
    testapp.post_json(
        '/in_vivo_system',
        {
            'lab': other_lab['@id'],
            'sample_terms': [controlled_term_brain['@id']],
            'classification': 'xenograft',
        },
        status=422
    )
    # Missing sample_terms
    testapp.post_json(
        '/in_vivo_system',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'classification': 'xenograft',
        },
        status=422
    )
    # Missing classification
    testapp.post_json(
        '/in_vivo_system',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
        },
        status=422
    )


def test_in_vivo_system_classification_enum(testapp, other_lab, human_donor, controlled_term_brain):
    testapp.post_json(
        '/in_vivo_system',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'classification': 'invalid_classification',
            'status': 'current',
        },
        status=422
    )


def test_in_vivo_system_host_linkto_validation(testapp, other_lab, human_donor, controlled_term_brain):
    # Invalid host reference
    testapp.post_json(
        '/in_vivo_system',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'classification': 'xenograft',
            'host': 'invalid-donor-id',
            'status': 'current',
        },
        status=422
    )


def test_in_vivo_system_create_success(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'classification': 'xenograft',
        'status': 'current',
    }
    res = testapp.post_json('/in_vivo_system', item, status=201)
    assert res.json['@graph'][0]['lab'] == other_lab['@id']
    assert res.json['@graph'][0]['donors'] == [human_donor['@id']]
    assert res.json['@graph'][0]['sample_terms'] == [controlled_term_brain['@id']]
    assert res.json['@graph'][0]['classification'] == 'xenograft'


def test_in_vivo_system_create_with_all_optional_fields(testapp, other_lab, human_donor, controlled_term_brain, non_human_donor):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'classification': 'xenograft',
        'host': non_human_donor['@id'],
        'description': 'Test in vivo system with all fields',
        'status': 'current',
    }
    res = testapp.post_json('/in_vivo_system', item, status=201)
    assert res.json['@graph'][0]['classification'] == 'xenograft'
    assert res.json['@graph'][0]['host'] == non_human_donor['@id']
    assert res.json['@graph'][0]['description'] == 'Test in vivo system with all fields'


@pytest.mark.parametrize(
    'classification',
    [
        'xenograft'
    ]
)
def test_in_vivo_system_create_with_classification_enum_values(testapp, other_lab, human_donor, controlled_term_brain, classification):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'classification': classification,
        'status': 'current',
    }
    res = testapp.post_json('/in_vivo_system', item, status=201)
    assert res.json['@graph'][0]['classification'] == classification
