import pytest


def test_experiment_summary_with_aliases(testapp, experiment_with_aliases):
    res = testapp.get(experiment_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:pytest-experiment-basic'


def test_experiment_summary_with_description(testapp, experiment_with_description):
    res = testapp.get(experiment_with_description['@id'])
    assert res.json.get('summary') == 'Test experiment grouping droplet libraries'


def test_experiment_summary_with_uuid(testapp, experiment):
    res = testapp.get(experiment['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


def test_experiment_required_fields(testapp, other_lab, droplet_based_library):
    testapp.post_json(
        '/experiment',
        {
            'libraries': [droplet_based_library['@id']],
        },
        status=422,
    )
    testapp.post_json(
        '/experiment',
        {
            'lab': other_lab['@id'],
        },
        status=422,
    )


def test_experiment_libraries_min_items(testapp, other_lab):
    testapp.post_json(
        '/experiment',
        {
            'lab': other_lab['@id'],
            'libraries': [],
            'status': 'current',
        },
        status=422,
    )


def test_experiment_libraries_unique_items(testapp, other_lab, droplet_based_library):
    testapp.post_json(
        '/experiment',
        {
            'lab': other_lab['@id'],
            'libraries': [
                droplet_based_library['@id'],
                droplet_based_library['@id'],
            ],
            'status': 'current',
        },
        status=422,
    )


def test_experiment_libraries_linkto_validation(testapp, other_lab):
    testapp.post_json(
        '/experiment',
        {
            'lab': other_lab['@id'],
            'libraries': ['/invalid/library/path/'],
            'status': 'current',
        },
        status=422,
    )


def test_experiment_create_with_droplet_library(testapp, other_lab, droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'libraries': [droplet_based_library['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/experiment', item, status=201)
    assert res.json['@graph'][0]['libraries'] == [droplet_based_library['@id']]


def test_experiment_create_with_plate_library(testapp, other_lab, plate_based_library):
    item = {
        'lab': other_lab['@id'],
        'libraries': [plate_based_library['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/experiment', item, status=201)
    assert res.json['@graph'][0]['libraries'] == [plate_based_library['@id']]


def test_experiment_create_with_mixed_libraries(
    testapp,
    other_lab,
    droplet_based_library,
    plate_based_library,
):
    item = {
        'lab': other_lab['@id'],
        'libraries': [
            droplet_based_library['@id'],
            plate_based_library['@id'],
        ],
        'status': 'current',
    }
    res = testapp.post_json('/experiment', item, status=201)
    assert len(res.json['@graph'][0]['libraries']) == 2


@pytest.mark.parametrize(
    'cro_experiment_identifier',
    [
        'CRO-BATCH-2024-01',
        'x',
        'group_A-1',
        'a\nb',
    ],
)
def test_experiment_cro_experiment_identifier_valid(
    testapp,
    other_lab,
    droplet_based_library,
    cro_experiment_identifier,
):
    item = {
        'lab': other_lab['@id'],
        'libraries': [droplet_based_library['@id']],
        'CRO_experiment_identifier': cro_experiment_identifier,
        'status': 'current',
    }
    res = testapp.post_json('/experiment', item, status=201)
    assert res.json['@graph'][0]['CRO_experiment_identifier'] == cro_experiment_identifier


@pytest.mark.parametrize(
    'cro_experiment_identifier',
    [
        '',
        ' ',
        '  ',
        ' leading',
        'trailing ',
        '\tleading-tab',
        'trailing-tab\t',
    ],
)
def test_experiment_cro_experiment_identifier_invalid(
    testapp,
    other_lab,
    droplet_based_library,
    cro_experiment_identifier,
):
    testapp.post_json(
        '/experiment',
        {
            'lab': other_lab['@id'],
            'libraries': [droplet_based_library['@id']],
            'CRO_experiment_identifier': cro_experiment_identifier,
            'status': 'current',
        },
        status=422,
    )


def test_experiment_create_with_all_optional_fields(
    testapp,
    other_lab,
    droplet_based_library,
    droplet_based_library_with_feature_types,
):
    item = {
        'lab': other_lab['@id'],
        'libraries': [
            droplet_based_library['@id'],
            droplet_based_library_with_feature_types['@id'],
        ],
        'description': 'Complete experiment with droplet libraries',
        'CRO_experiment_identifier': 'CRO-EXP-001',
        'aliases': ['lattice:pytest-experiment-complete'],
        'status': 'current',
    }
    res = testapp.post_json('/experiment', item, status=201)
    assert len(res.json['@graph'][0]['libraries']) == 2
    assert res.json['@graph'][0]['description'] == 'Complete experiment with droplet libraries'
    assert res.json['@graph'][0]['CRO_experiment_identifier'] == 'CRO-EXP-001'
    assert res.json['@graph'][0]['aliases'] == ['lattice:pytest-experiment-complete']
