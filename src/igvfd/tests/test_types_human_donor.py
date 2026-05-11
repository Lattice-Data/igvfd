import pytest


def test_human_donor_summary_with_aliases(testapp, human_donor_with_aliases):
    res = testapp.get(human_donor_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:pytest-human-donor-summary-alias'


def test_human_donor_summary_with_description(testapp, human_donor_with_description):
    res = testapp.get(human_donor_with_description['@id'])
    assert res.json.get('summary') == 'Test human donor'


def test_human_donor_summary_with_uuid(testapp, human_donor):
    res = testapp.get(human_donor['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


def test_human_donor_required_fields(testapp, other_lab):
    cxg = 'lattice:test-cxg-human-required'
    # Test that taxa is required
    testapp.post_json(
        '/human_donor',
        {
            'lab': other_lab['@id'],
            'cxg_donor_id': cxg,
        },
        status=422
    )
    # Test that lab is required
    testapp.post_json(
        '/human_donor',
        {
            'taxa': 'Homo sapiens',
            'cxg_donor_id': cxg,
        },
        status=422
    )
    # cxg_donor_id is required
    testapp.post_json(
        '/human_donor',
        {
            'lab': other_lab['@id'],
            'taxa': 'Homo sapiens',
        },
        status=422,
    )


@pytest.mark.parametrize(
    'invalid_cxg',
    [
        '',
        '   ',
        'na',
        'N/A',
        'null',
        'Unknown',
        'unspecified',
        'none',
        'tbd',
        'not applicable',
    ]
)
def test_human_donor_cxg_id_pattern_invalid(testapp, other_lab, invalid_cxg):
    testapp.post_json(
        '/human_donor',
        {
            'lab': other_lab['@id'],
            'taxa': 'Homo sapiens',
            'cxg_donor_id': invalid_cxg,
            'status': 'current',
        },
        status=422,
    )


def test_human_donor_cxg_migration_placeholder_accepted(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'cxg_donor_id': 'placeholder cxg donor id',
        'status': 'current',
    }
    res = testapp.post_json('/human_donor', item, status=201)
    assert res.json['@graph'][0]['cxg_donor_id'] == 'placeholder cxg donor id'


def test_human_donor_taxa_enum(testapp, other_lab):
    # Test that only 'Homo sapiens' is allowed
    testapp.post_json(
        '/human_donor',
        {
            'lab': other_lab['@id'],
            'taxa': 'Mus musculus',
            'cxg_donor_id': 'lattice:test-cxg-taxa-invalid',
            'status': 'current',
        },
        status=422
    )


def test_human_donor_create(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'cxg_donor_id': 'CXG-human-create-01',
        'status': 'current',
    }
    res = testapp.post_json('/human_donor', item, status=201)
    assert res.json['@graph'][0]['taxa'] == 'Homo sapiens'
    assert res.json['@graph'][0]['lab'] == other_lab['@id']


def test_human_donor_author_metadata(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'cxg_donor_id': 'CXG-human-author-metadata',
        'author_metadata': {
            'external_subject_id': 'HD-TEST-001',
            'is_case': True,
            'age_at_collection_days': 42,
        },
        'status': 'current',
    }
    res = testapp.post_json('/human_donor', item, status=201)
    assert res.json['@graph'][0]['author_metadata'] == item['author_metadata']


@pytest.mark.parametrize('sex', ['male', 'female', 'unspecified', 'mixed'])
def test_human_donor_sex_enum_valid(testapp, other_lab, sex):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'sex': sex,
        'cxg_donor_id': f'lattice:test-cxg-human-sex-{sex}',
        'status': 'current',
    }
    res = testapp.post_json('/human_donor', item, status=201)
    assert res.json['@graph'][0]['sex'] == sex


def test_human_donor_sex_enum_invalid(testapp, other_lab):
    testapp.post_json(
        '/human_donor',
        {
            'lab': other_lab['@id'],
            'taxa': 'Homo sapiens',
            'sex': 'not-a-real-sex',
            'cxg_donor_id': 'CXG-human-sex-invalid',
            'status': 'current',
        },
        status=422,
    )
