import pytest


def test_non_human_donor_summary_with_aliases(testapp, non_human_donor_with_aliases):
    res = testapp.get(non_human_donor_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:test-non-human-donor-1'


def test_non_human_donor_summary_with_description(testapp, non_human_donor_with_description):
    res = testapp.get(non_human_donor_with_description['@id'])
    assert res.json.get('summary') == 'Test non human donor'


def test_non_human_donor_summary_with_uuid(testapp, non_human_donor):
    res = testapp.get(non_human_donor['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


def test_non_human_donor_required_fields(testapp, other_lab):
    testapp.post_json(
        '/non_human_donor',
        {
            'lab': other_lab['@id'],
        },
        status=422
    )
    testapp.post_json(
        '/non_human_donor',
        {
            'taxa': 'Mus musculus',
        },
        status=422
    )


def test_non_human_donor_taxa_enum(testapp, other_lab):
    testapp.post_json(
        '/non_human_donor',
        {
            'lab': other_lab['@id'],
            'taxa': 'Homo sapiens',
        },
        status=422
    )


@pytest.mark.parametrize(
    'taxa',
    [
        'Mus musculus',
        'Ciona intestinalis',
        'Petromyzon marinus',
    ]
)
def test_non_human_donor_create_with_enum_values(testapp, other_lab, taxa):
    item = {
        'lab': other_lab['@id'],
        'taxa': taxa,
        'status': 'current',
    }
    res = testapp.post_json('/non_human_donor', item, status=201)
    assert res.json['@graph'][0]['taxa'] == taxa
    assert res.json['@graph'][0]['lab'] == other_lab['@id']


@pytest.mark.parametrize(
    'taxa,sex',
    [
        ('Mus musculus', 'female'),
        ('Mus musculus', 'male'),
        ('Mus musculus', 'mixed'),
        ('Mus musculus', 'unspecified'),
        ('Danio rerio', 'female'),
        ('Xenopus tropicalis', 'male'),
    ]
)
def test_non_human_donor_sex_valid_gonochoristic(testapp, other_lab, taxa, sex):
    item = {
        'lab': other_lab['@id'],
        'taxa': taxa,
        'sex': sex,
        'status': 'current',
    }
    res = testapp.post_json('/non_human_donor', item, status=201)
    assert res.json['@graph'][0]['sex'] == sex


@pytest.mark.parametrize(
    'taxa,sex',
    [
        ('Ciona intestinalis', 'hermaphrodite'),
        ('Ciona intestinalis', 'female'),
        ('Ciona intestinalis', 'male'),
        ('Ciona intestinalis', 'mixed'),
        ('Ciona intestinalis', 'unspecified'),
        ('Beroe ovata', 'hermaphrodite'),
        ('Sycon ciliatum', 'hermaphrodite'),
        ('Myxine glutinosa', 'hermaphrodite'),
    ]
)
def test_non_human_donor_sex_valid_hermaphroditic(testapp, other_lab, taxa, sex):
    item = {
        'lab': other_lab['@id'],
        'taxa': taxa,
        'sex': sex,
        'status': 'current',
    }
    res = testapp.post_json('/non_human_donor', item, status=201)
    assert res.json['@graph'][0]['sex'] == sex


@pytest.mark.parametrize(
    'taxa,sex',
    [
        ('Mus musculus', 'hermaphrodite'),
        ('Danio rerio', 'hermaphrodite'),
        ('Xenopus tropicalis', 'hermaphrodite'),
    ]
)
def test_non_human_donor_sex_invalid_hermaphrodite_on_gonochoristic(testapp, other_lab, taxa, sex):
    testapp.post_json(
        '/non_human_donor',
        {
            'lab': other_lab['@id'],
            'taxa': taxa,
            'sex': sex,
            'status': 'current',
        },
        status=422,
    )


def test_non_human_donor_sex_invalid_value(testapp, other_lab):
    testapp.post_json(
        '/non_human_donor',
        {
            'lab': other_lab['@id'],
            'taxa': 'Mus musculus',
            'sex': 'not-a-real-sex',
            'status': 'current',
        },
        status=422,
    )


def test_non_human_donor_sex_default(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Mus musculus',
        'status': 'current',
    }
    res = testapp.post_json('/non_human_donor', item, status=201)
    assert res.json['@graph'][0]['sex'] == 'unspecified'
