import pytest


def test_human_donor_summary_with_aliases(testapp, human_donor_with_aliases):
    res = testapp.get(human_donor_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:human-donor-european'


def test_human_donor_summary_with_description(testapp, human_donor_with_description):
    res = testapp.get(human_donor_with_description['@id'])
    assert res.json.get('summary') == 'Test human donor'


def test_human_donor_summary_with_uuid(testapp, human_donor):
    res = testapp.get(human_donor['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


def test_human_donor_required_fields(testapp, other_lab):
    # Test that taxa is required
    testapp.post_json(
        '/human_donor',
        {
            'lab': other_lab['@id'],
        },
        status=422
    )
    # Test that lab is required
    testapp.post_json(
        '/human_donor',
        {
            'taxa': 'Homo sapiens',
        },
        status=422
    )


def test_human_donor_taxa_enum(testapp, other_lab):
    # Test that only 'Homo sapiens' is allowed
    testapp.post_json(
        '/human_donor',
        {
            'lab': other_lab['@id'],
            'taxa': 'Mus musculus',
        },
        status=422
    )


def test_human_donor_create(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'status': 'current',
    }
    res = testapp.post_json('/human_donor', item, status=201)
    assert res.json['@graph'][0]['taxa'] == 'Homo sapiens'
    assert res.json['@graph'][0]['lab'] == other_lab['@id']


@pytest.mark.parametrize('sex', ['male', 'female', 'unspecified', 'mixed'])
def test_human_donor_sex_enum_valid(testapp, other_lab, sex):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Homo sapiens',
        'sex': sex,
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
            'status': 'current',
        },
        status=422,
    )
