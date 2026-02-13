import pytest


# Biosample type configurations
BIOSAMPLE_CONFIGS = {
    'tissue': {
        'endpoint': '/tissue',
        'fixture_alias': 'lattice:tissue-brain-coronal',
        'fixture_description': 'Test tissue sample',
        'has_classification': False,
        'has_intended_cell_types': False,
    },
    'in_vitro_system': {
        'endpoint': '/in_vitro_system',
        'fixture_alias': 'lattice:in-vitro-organoid',
        'fixture_description': 'Test in vitro system sample',
        'has_classification': True,
        'classification_value': 'organoid',
        'has_intended_cell_types': True,
    },
    'in_vivo_system': {
        'endpoint': '/in_vivo_system',
        'fixture_alias': 'lattice:in-vivo-xenograft',
        'fixture_description': 'Test in vivo system sample',
        'has_classification': True,
        'classification_value': 'xenograft',
        'has_intended_cell_types': True,
    },
}


@pytest.mark.parametrize('biosample_type', ['tissue', 'in_vitro_system', 'in_vivo_system'])
def test_biosample_summary_with_aliases(testapp, biosample_type, request):
    config = BIOSAMPLE_CONFIGS[biosample_type]
    fixture = request.getfixturevalue(f'{biosample_type}_with_aliases')
    res = testapp.get(fixture['@id'])
    assert res.json.get('summary') == config['fixture_alias']


@pytest.mark.parametrize('biosample_type', ['tissue', 'in_vitro_system', 'in_vivo_system'])
def test_biosample_summary_with_description(testapp, biosample_type, request):
    config = BIOSAMPLE_CONFIGS[biosample_type]
    fixture = request.getfixturevalue(f'{biosample_type}_with_description')
    res = testapp.get(fixture['@id'])
    assert res.json.get('summary') == config['fixture_description']


@pytest.mark.parametrize('biosample_type', ['tissue', 'in_vitro_system', 'in_vivo_system'])
def test_biosample_summary_with_uuid(testapp, biosample_type, request):
    config = BIOSAMPLE_CONFIGS[biosample_type]
    fixture = request.getfixturevalue(biosample_type)
    res = testapp.get(fixture['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


@pytest.mark.parametrize('biosample_type', ['tissue', 'in_vitro_system', 'in_vivo_system'])
def test_biosample_required_fields(testapp, other_lab, human_donor, controlled_term_brain, biosample_type):
    config = BIOSAMPLE_CONFIGS[biosample_type]
    endpoint = config['endpoint']

    # Base payload for tests
    base_payload = {
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
    }
    if config['has_classification']:
        base_payload['classification'] = config['classification_value']

    # Missing lab
    payload = base_payload.copy()
    testapp.post_json(endpoint, payload, status=422)

    # Missing donors
    payload = {'lab': other_lab['@id'], 'sample_terms': [controlled_term_brain['@id']]}
    if config['has_classification']:
        payload['classification'] = config['classification_value']
    testapp.post_json(endpoint, payload, status=422)

    # Missing sample_terms
    payload = {'lab': other_lab['@id'], 'donors': [human_donor['@id']]}
    if config['has_classification']:
        payload['classification'] = config['classification_value']
    testapp.post_json(endpoint, payload, status=422)

    # Missing classification (only for in_vitro_system and in_vivo_system)
    if config['has_classification']:
        payload = {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
        }
        testapp.post_json(endpoint, payload, status=422)


@pytest.mark.parametrize('biosample_type', ['in_vitro_system', 'in_vivo_system'])
def test_biosample_create_with_intended_cell_types(testapp, other_lab, human_donor,
                                                   controlled_term_brain, controlled_term, biosample_type):
    config = BIOSAMPLE_CONFIGS[biosample_type]
    endpoint = config['endpoint']

    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'classification': config['classification_value'],
        'intended_cell_types': [controlled_term['@id']],
        'status': 'current',
    }
    res = testapp.post_json(endpoint, item, status=201)
    assert res.json['@graph'][0]['intended_cell_types'] == [controlled_term['@id']]


@pytest.mark.parametrize('biosample_type', ['in_vitro_system', 'in_vivo_system'])
def test_biosample_intended_cell_types_min_items(testapp, other_lab, human_donor,
                                                 controlled_term_brain, biosample_type):
    config = BIOSAMPLE_CONFIGS[biosample_type]
    endpoint = config['endpoint']

    testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'classification': config['classification_value'],
            'intended_cell_types': [],
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize('biosample_type', ['in_vitro_system', 'in_vivo_system'])
def test_biosample_intended_cell_types_unique_items(testapp, other_lab, human_donor,
                                                    controlled_term_brain, controlled_term, biosample_type):
    config = BIOSAMPLE_CONFIGS[biosample_type]
    endpoint = config['endpoint']

    testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'classification': config['classification_value'],
            'intended_cell_types': [controlled_term['@id'], controlled_term['@id']],
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize('biosample_type', ['in_vitro_system', 'in_vivo_system'])
def test_biosample_intended_cell_types_linkto_validation(testapp, other_lab, human_donor,
                                                         controlled_term_brain, biosample_type):
    config = BIOSAMPLE_CONFIGS[biosample_type]
    endpoint = config['endpoint']

    testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'classification': config['classification_value'],
            'intended_cell_types': ['/invalid/term/path/'],
            'status': 'current',
        },
        status=422
    )
