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
    'organoid': {
        'endpoint': '/organoid',
        'fixture_alias': 'lattice:organoid-brain-model',
        'fixture_description': 'Test organoid sample',
        'has_classification': False,
        'has_intended_cell_types': True,
    },
    'cell_line': {
        'endpoint': '/cell_line',
        'fixture_alias': 'lattice:cell-line-immortalized',
        'fixture_description': 'Test cell line sample',
        'has_classification': False,
        'has_intended_cell_types': True,
    },
}


def _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type):
    if biosample_type == 'primary_cell_culture':
        return '/primary_cell_culture', {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
        }

    config = BIOSAMPLE_CONFIGS[biosample_type]
    payload = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
    }
    if config['has_classification']:
        payload['classification'] = config['classification_value']
    return config['endpoint'], payload


@pytest.mark.parametrize('biosample_type', ['tissue', 'organoid', 'cell_line'])
def test_biosample_summary_with_aliases(testapp, biosample_type, request):
    config = BIOSAMPLE_CONFIGS[biosample_type]
    fixture = request.getfixturevalue(f'{biosample_type}_with_aliases')
    res = testapp.get(fixture['@id'])
    assert res.json.get('summary') == config['fixture_alias']


@pytest.mark.parametrize('biosample_type', ['tissue', 'organoid', 'cell_line'])
def test_biosample_summary_with_description(testapp, biosample_type, request):
    config = BIOSAMPLE_CONFIGS[biosample_type]
    fixture = request.getfixturevalue(f'{biosample_type}_with_description')
    res = testapp.get(fixture['@id'])
    assert res.json.get('summary') == config['fixture_description']


@pytest.mark.parametrize('biosample_type', ['tissue', 'organoid', 'cell_line'])
def test_biosample_summary_with_uuid(testapp, biosample_type, request):
    config = BIOSAMPLE_CONFIGS[biosample_type]
    fixture = request.getfixturevalue(biosample_type)
    res = testapp.get(fixture['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


@pytest.mark.parametrize('biosample_type', ['tissue', 'organoid', 'cell_line'])
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


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
def test_biosample_date_obtained_accepts_valid_date(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['date_obtained'] = '2024-03-01'
    payload['status'] = 'current'
    res = testapp.post_json(endpoint, payload, status=201)
    assert res.json['@graph'][0]['date_obtained'] == '2024-03-01'


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
def test_biosample_date_obtained_rejects_invalid_format(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['date_obtained'] = 'invalid-date'
    payload['status'] = 'current'
    testapp.post_json(endpoint, payload, status=422)


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
def test_biosample_collection_geographical_location_accepts_valid_enum(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['collection_geographical_location'] = 'Canada'
    payload['status'] = 'current'
    res = testapp.post_json(endpoint, payload, status=201)
    assert res.json['@graph'][0]['collection_geographical_location'] == 'Canada'


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
def test_biosample_collection_geographical_location_rejects_invalid_enum(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['collection_geographical_location'] = 'Atlantis'
    payload['status'] = 'current'
    testapp.post_json(endpoint, payload, status=422)


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
def test_biosample_collection_fields_are_optional(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['status'] = 'current'
    res = testapp.post_json(endpoint, payload, status=201)
    assert res.json['@graph'][0].get('date_obtained') is None
    assert res.json['@graph'][0].get('collection_geographical_location') is None


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
def test_biosample_diseases_accepts_controlled_term_links(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['diseases'] = [controlled_term_brain['@id']]
    payload['status'] = 'current'
    res = testapp.post_json(endpoint, payload, status=201)
    assert res.json['@graph'][0]['diseases'] == [controlled_term_brain['@id']]


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
def test_biosample_diseases_rejects_duplicate_values(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['diseases'] = [controlled_term_brain['@id'], controlled_term_brain['@id']]
    payload['status'] = 'current'
    testapp.post_json(endpoint, payload, status=422)


@pytest.mark.parametrize('biosample_type', ['organoid', 'cell_line'])
def test_biosample_create_with_intended_cell_types(testapp, other_lab, human_donor,
                                                   controlled_term_brain, controlled_term, biosample_type):
    config = BIOSAMPLE_CONFIGS[biosample_type]
    endpoint = config['endpoint']

    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'intended_cell_types': [controlled_term['@id']],
        'status': 'current',
    }
    if config['has_classification']:
        item['classification'] = config['classification_value']
    res = testapp.post_json(endpoint, item, status=201)
    assert res.json['@graph'][0]['intended_cell_types'] == [controlled_term['@id']]


@pytest.mark.parametrize('biosample_type', ['organoid', 'cell_line'])
def test_biosample_intended_cell_types_min_items(testapp, other_lab, human_donor,
                                                 controlled_term_brain, biosample_type):
    config = BIOSAMPLE_CONFIGS[biosample_type]
    endpoint = config['endpoint']

    payload = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'intended_cell_types': [],
        'status': 'current',
    }
    if config['has_classification']:
        payload['classification'] = config['classification_value']
    testapp.post_json(endpoint, payload, status=422)


@pytest.mark.parametrize('biosample_type', ['organoid', 'cell_line'])
def test_biosample_intended_cell_types_unique_items(testapp, other_lab, human_donor,
                                                    controlled_term_brain, controlled_term, biosample_type):
    config = BIOSAMPLE_CONFIGS[biosample_type]
    endpoint = config['endpoint']

    payload = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'intended_cell_types': [controlled_term['@id'], controlled_term['@id']],
        'status': 'current',
    }
    if config['has_classification']:
        payload['classification'] = config['classification_value']
    testapp.post_json(endpoint, payload, status=422)


@pytest.mark.parametrize('biosample_type', ['organoid', 'cell_line'])
def test_biosample_intended_cell_types_linkto_validation(testapp, other_lab, human_donor,
                                                         controlled_term_brain, biosample_type):
    config = BIOSAMPLE_CONFIGS[biosample_type]
    endpoint = config['endpoint']

    payload = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'intended_cell_types': ['/invalid/term/path/'],
        'status': 'current',
    }
    if config['has_classification']:
        payload['classification'] = config['classification_value']
    testapp.post_json(endpoint, payload, status=422)


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
def test_biosample_author_metadata(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type
):
    if biosample_type == 'primary_cell_culture':
        endpoint = '/primary_cell_culture'
        item = {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'author_metadata': {
                'batch_id': 'B-001',
                'prep_notes': 'test',
            },
            'status': 'current',
        }
    else:
        config = BIOSAMPLE_CONFIGS[biosample_type]
        endpoint = config['endpoint']
        item = {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'author_metadata': {
                'batch_id': 'B-001',
                'prep_notes': 'test',
            },
            'status': 'current',
        }
        if config['has_classification']:
            item['classification'] = config['classification_value']
    res = testapp.post_json(endpoint, item, status=201)
    assert res.json['@graph'][0]['author_metadata'] == item['author_metadata']
