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


def test_non_human_donor_required_fields(testapp, other_lab, taxon_mus_musculus):
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
            'taxa': taxon_mus_musculus['@id'],
            'cxg_donor_id': cxg,
        },
        status=422
    )
    testapp.post_json(
        '/non_human_donor',
        {
            'lab': other_lab['@id'],
            'taxa': taxon_mus_musculus['@id'],
        },
        status=422,
    )


def test_non_human_donor_taxa_rejects_homo_sapiens(testapp, other_lab, taxon_homo_sapiens):
    res = testapp.post_json(
        '/non_human_donor',
        {
            'lab': other_lab['@id'],
            'taxa': taxon_homo_sapiens['@id'],
            'cxg_donor_id': 'CXG-nhd-taxa-reject',
            'status': 'current',
        },
        status=422
    )
    assert any(
        error['name'] == ['taxa'] and 'Mus musculus (NCBITaxon:10090)' in error['description']
        for error in res.json['errors']
    )


def test_non_human_donor_taxa_rejects_unlisted_species(testapp, other_lab, post_taxon):
    # Rattus norvegicus is an NCBITaxon term the schema does not list.
    taxon = post_taxon('NCBITaxon:10116')
    testapp.post_json(
        '/non_human_donor',
        {
            'lab': other_lab['@id'],
            'taxa': taxon['@id'],
            'cxg_donor_id': 'CXG-nhd-taxa-unlisted',
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
def test_non_human_donor_cxg_id_pattern_invalid(testapp, other_lab, invalid_cxg, taxon_mus_musculus):
    testapp.post_json(
        '/non_human_donor',
        {
            'lab': other_lab['@id'],
            'taxa': taxon_mus_musculus['@id'],
            'cxg_donor_id': invalid_cxg,
            'status': 'current',
        },
        status=422,
    )


@pytest.mark.parametrize(
    'term_id',
    [
        'NCBITaxon:10090',  # Mus musculus
        'NCBITaxon:7719',  # Ciona intestinalis
        'NCBITaxon:7757',  # Petromyzon marinus
    ]
)
def test_non_human_donor_create_with_allowed_taxa(testapp, other_lab, post_taxon, term_id):
    taxon = post_taxon(term_id)
    item = {
        'lab': other_lab['@id'],
        'taxa': taxon['@id'],
        'cxg_donor_id': 'lattice:test-cxg-nhd-' + term_id.replace(':', '-'),
        'status': 'current',
    }
    res = testapp.post_json('/non_human_donor', item, status=201)
    assert res.json['@graph'][0]['taxa'] == taxon['@id']
    assert res.json['@graph'][0]['lab'] == other_lab['@id']


def test_non_human_donor_author_metadata(testapp, other_lab, taxon_mus_musculus):
    item = {
        'lab': other_lab['@id'],
        'taxa': taxon_mus_musculus['@id'],
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
    'term_id,sex',
    [
        ('NCBITaxon:10090', 'female'),  # Mus musculus
        ('NCBITaxon:10090', 'male'),
        ('NCBITaxon:10090', 'mixed'),
        ('NCBITaxon:10090', 'unspecified'),
        ('NCBITaxon:7955', 'female'),  # Danio rerio
        ('NCBITaxon:7719', 'hermaphrodite'),  # Ciona intestinalis
        ('NCBITaxon:7719', 'female'),
        ('NCBITaxon:10201', 'hermaphrodite'),  # Beroe ovata
        ('NCBITaxon:27933', 'hermaphrodite'),  # Sycon ciliatum
        ('NCBITaxon:7769', 'hermaphrodite'),  # Myxine glutinosa
        # Accepted, and flagged by audit_non_human_donor_hermaphrodite_sex instead.
        ('NCBITaxon:10090', 'hermaphrodite'),
        ('NCBITaxon:8364', 'hermaphrodite'),  # Xenopus tropicalis
    ]
)
def test_non_human_donor_sex_accepted_for_any_taxa(testapp, other_lab, post_taxon, term_id, sex):
    taxon = post_taxon(term_id)
    item = {
        'lab': other_lab['@id'],
        'taxa': taxon['@id'],
        'sex': sex,
        'cxg_donor_id': 'lattice:test-cxg-sex-{0}-{1}'.format(term_id.replace(':', '-'), sex),
        'status': 'current',
    }
    res = testapp.post_json('/non_human_donor', item, status=201)
    assert res.json['@graph'][0]['sex'] == sex


def test_non_human_donor_sex_invalid_value(testapp, other_lab, taxon_mus_musculus):
    testapp.post_json(
        '/non_human_donor',
        {
            'lab': other_lab['@id'],
            'taxa': taxon_mus_musculus['@id'],
            'sex': 'not-a-real-sex',
            'cxg_donor_id': 'CXG-nhd-invalid-sex',
            'status': 'current',
        },
        status=422,
    )


def test_non_human_donor_sex_default(testapp, other_lab, taxon_mus_musculus):
    item = {
        'lab': other_lab['@id'],
        'taxa': taxon_mus_musculus['@id'],
        'cxg_donor_id': 'CXG-nhd-default-sex',
        'status': 'current',
    }
    res = testapp.post_json('/non_human_donor', item, status=201)
    assert res.json['@graph'][0]['sex'] == 'unspecified'
