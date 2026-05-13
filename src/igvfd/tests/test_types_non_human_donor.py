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
    cxg = 'lattice:test-cxg-nhd-req-base'
    testapp.post_json(
        '/non_human_donor',
        {
            'lab': other_lab['@id'],
            'cxg_donor_id': cxg,
        },
        status=422
    )
    testapp.post_json(
        '/non_human_donor',
        {
            'taxa': 'Mus musculus',
            'cxg_donor_id': cxg,
        },
        status=422
    )
    testapp.post_json(
        '/non_human_donor',
        {
            'lab': other_lab['@id'],
            'taxa': 'Mus musculus',
        },
        status=422,
    )


def test_non_human_donor_taxa_enum(testapp, other_lab):
    testapp.post_json(
        '/non_human_donor',
        {
            'lab': other_lab['@id'],
            'taxa': 'Homo sapiens',
            'cxg_donor_id': 'CXG-nhd-taxa-reject',
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize(
    'invalid_cxg',
    [
        '',
        'na',
        'Unknown',
        'unspecified',
    ]
)
def test_non_human_donor_cxg_id_pattern_invalid(testapp, other_lab, invalid_cxg):
    testapp.post_json(
        '/non_human_donor',
        {
            'lab': other_lab['@id'],
            'taxa': 'Mus musculus',
            'cxg_donor_id': invalid_cxg,
            'status': 'current',
        },
        status=422,
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
    slug = taxa.replace(' ', '-').lower()
    item = {
        'lab': other_lab['@id'],
        'taxa': taxa,
        'cxg_donor_id': f'lattice:test-cxg-nhd-{slug}',
        'status': 'current',
    }
    res = testapp.post_json('/non_human_donor', item, status=201)
    assert res.json['@graph'][0]['taxa'] == taxa
    assert res.json['@graph'][0]['lab'] == other_lab['@id']


def test_non_human_donor_author_metadata(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Mus musculus',
        'cxg_donor_id': 'CXG-nhd-author-meta',
        'author_metadata': {
            'source_colony': 'SPF',
            'age_weeks': 12,
            'paired_litter': False,
        },
        'status': 'current',
    }
    res = testapp.post_json('/non_human_donor', item, status=201)
    assert res.json['@graph'][0]['author_metadata'] == item['author_metadata']


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
    slug = taxa.replace(' ', '-').lower()
    cxg = 'lattice:test-cxg-gon-{0}-{1}'.format(slug, sex.replace(' ', '_'))
    item = {
        'lab': other_lab['@id'],
        'taxa': taxa,
        'sex': sex,
        'cxg_donor_id': cxg,
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
    slug = taxa.replace(' ', '-').lower()
    cxg = 'lattice:test-cxg-herm-{0}-{1}'.format(slug, sex.replace(' ', '_'))
    item = {
        'lab': other_lab['@id'],
        'taxa': taxa,
        'sex': sex,
        'cxg_donor_id': cxg,
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
            'cxg_donor_id': 'CXG-nhd-invalid-herm',
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
            'cxg_donor_id': 'CXG-nhd-invalid-sex',
            'status': 'current',
        },
        status=422,
    )


def test_non_human_donor_sex_default(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'taxa': 'Mus musculus',
        'cxg_donor_id': 'CXG-nhd-default-sex',
        'status': 'current',
    }
    res = testapp.post_json('/non_human_donor', item, status=201)
    assert res.json['@graph'][0]['sex'] == 'unspecified'
