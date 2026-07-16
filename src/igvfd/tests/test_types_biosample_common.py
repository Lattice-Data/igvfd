import pytest


# Biosample type configurations
BIOSAMPLE_CONFIGS = {
    'tissue': {
        'endpoint': '/tissue',
        'fixture_alias': 'lattice:pytest-tissue-brain-coronal-fixture',
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
def test_biosample_dbxrefs_accepts_valid_values(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['dbxrefs'] = ['BioSample:SAMEA1234567', 'SRA:SRS12345']
    payload['status'] = 'current'
    res = testapp.post_json(endpoint, payload, status=201)
    assert res.json['@graph'][0]['dbxrefs'] == ['BioSample:SAMEA1234567', 'SRA:SRS12345']


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
def test_biosample_dbxrefs_rejects_invalid_values(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['dbxrefs'] = ['GEO:GSM12345']
    payload['status'] = 'current'
    testapp.post_json(endpoint, payload, status=422)


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
@pytest.mark.parametrize(
    'multiplexing_barcodes',
    [
        ['P01-A1'],
        ['SCALE-A1'],
        ['BC001'],
        ['A-A01'],
        ['9A-9C'],
        ['A0251'],
    ],
)
def test_biosample_multiplexing_barcodes_valid(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type, multiplexing_barcodes
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['multiplexing_barcodes'] = multiplexing_barcodes
    payload['status'] = 'current'
    res = testapp.post_json(endpoint, payload, status=201)
    assert res.json['@graph'][0]['multiplexing_barcodes'] == multiplexing_barcodes


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
@pytest.mark.parametrize(
    'multiplexing_barcodes',
    [
        [],
        [''],
        [' '],
        [' P01-A1'],
        ['P01-A1 '],
        ['\tP01'],
        ['P01 A1'],
        ['P01\nA1'],
        ['-P01'],
        ['_only'],
        ['---'],
        ['x'],
        ['group_A-1'],
        ['A1_B2'],
    ],
)
def test_biosample_multiplexing_barcodes_invalid(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type, multiplexing_barcodes
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['multiplexing_barcodes'] = multiplexing_barcodes
    payload['status'] = 'current'
    testapp.post_json(endpoint, payload, status=422)


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
@pytest.mark.parametrize(
    'RT_indexes',
    [
        ['SCALEQUANT-A1'],
        ['SCALEQUANT-A1', 'SCALEQUANT-A2', 'SCALEQUANT-A3', 'SCALEQUANT-A4'],
        ['P01-A1', 'P01-A2'],
        ['P01-A1', 'P01-B12', 'P02-C3'],
    ],
)
def test_biosample_rt_indexes_valid(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type, RT_indexes
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['RT_indexes'] = RT_indexes
    payload['status'] = 'current'
    res = testapp.post_json(endpoint, payload, status=201)
    assert res.json['@graph'][0]['RT_indexes'] == RT_indexes


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
@pytest.mark.parametrize(
    'RT_indexes',
    [
        [],
        [''],
        [' '],
        ['P01 A1'],
        [' P01-A1'],
        ['P01-A1 '],
        ['P01-'],
        ['-A1'],
        ['P01'],
        ['---'],
    ],
)
def test_biosample_rt_indexes_invalid(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type, RT_indexes
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['RT_indexes'] = RT_indexes
    payload['status'] = 'current'
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
def test_biosample_developmental_stages_accepts_controlled_term_links(
    testapp, other_lab, human_donor, controlled_term_brain, controlled_term_dev_stage_human, biosample_type
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['developmental_stages'] = [controlled_term_dev_stage_human['@id']]
    payload['status'] = 'current'
    res = testapp.post_json(endpoint, payload, status=201)
    assert res.json['@graph'][0]['developmental_stages'] == [controlled_term_dev_stage_human['@id']]


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
def test_biosample_developmental_stages_rejects_invalid_path(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['developmental_stages'] = ['/invalid/term/path/']
    payload['status'] = 'current'
    testapp.post_json(endpoint, payload, status=422)


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
def test_biosample_developmental_stages_rejects_empty_array(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['developmental_stages'] = []
    payload['status'] = 'current'
    testapp.post_json(endpoint, payload, status=422)


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
def test_biosample_developmental_stages_rejects_duplicate_values(
    testapp, other_lab, human_donor, controlled_term_brain, controlled_term_dev_stage_human, biosample_type
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['developmental_stages'] = [
        controlled_term_dev_stage_human['@id'],
        controlled_term_dev_stage_human['@id'],
    ]
    payload['status'] = 'current'
    testapp.post_json(endpoint, payload, status=422)


@pytest.mark.parametrize(
    'biosample_type',
    ['tissue', 'primary_cell_culture', 'organoid', 'cell_line'],
)
def test_biosample_developmental_stages_is_optional(
    testapp, other_lab, human_donor, controlled_term_brain, biosample_type
):
    endpoint, payload = _make_biosample_payload(other_lab, human_donor, controlled_term_brain, biosample_type)
    payload['status'] = 'current'
    res = testapp.post_json(endpoint, payload, status=201)
    assert res.json['@graph'][0].get('developmental_stages') is None


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


def test_biosample_libraries_reverse_link_plate_based_library(
    testapp, tissue, plate_based_library,
):
    res = testapp.get(tissue['@id'])
    assert plate_based_library['@id'] in res.json['libraries']


def test_biosample_libraries_reverse_link_droplet_based_library(
    testapp, tissue, droplet_based_library,
):
    res = testapp.get(tissue['@id'])
    assert droplet_based_library['@id'] in res.json['libraries']


def test_biosample_libraries_reverse_link_multiple_libraries(
    testapp, other_lab, tissue, plate_based_library, droplet_based_library,
):
    second_plate_library = testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'status': 'current',
        },
        status=201,
    ).json['@graph'][0]

    res = testapp.get(tissue['@id'])
    libraries = res.json['libraries']
    assert len(libraries) == 3
    assert plate_based_library['@id'] in libraries
    assert droplet_based_library['@id'] in libraries
    assert second_plate_library['@id'] in libraries


def test_biosample_libraries_reverse_link_no_libraries(
    testapp, other_lab, human_donor, controlled_term_brain,
):
    tissue = testapp.post_json(
        '/tissue',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'status': 'current',
        },
        status=201,
    ).json['@graph'][0]

    res = testapp.get(tissue['@id'])
    assert res.json['libraries'] == []


@pytest.mark.parametrize(
    'endpoint,sample_term_fixture',
    [
        ('/organoid', 'controlled_term_brain'),
        ('/cell_line', 'controlled_term'),
    ],
)
def test_biosample_libraries_reverse_link_inherited(
    testapp, other_lab, human_donor, endpoint, sample_term_fixture, request,
):
    sample_term = request.getfixturevalue(sample_term_fixture)
    biosample = testapp.post_json(
        endpoint,
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [sample_term['@id']],
            'status': 'current',
        },
        status=201,
    ).json['@graph'][0]

    linked_library = testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [biosample['@id']],
            'status': 'current',
        },
        status=201,
    ).json['@graph'][0]

    res = testapp.get(biosample['@id'])
    assert linked_library['@id'] in res.json['libraries']
