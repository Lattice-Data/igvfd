import pytest

from igvfd.audit.donor import audit_non_human_donor_hermaphrodite_sex


def _audit_errors(res):
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    return errors_list


def _donor(sex, term_id):
    return {
        '@type': ['NonHumanDonor'],
        '@id': '/non-human-donors/IGVFDTEST0001/',
        'sex': sex,
        'taxa': {
            '@id': f'/controlled_terms/{term_id}/',
            'term_id': term_id,
        },
    }


@pytest.mark.parametrize(
    'sex,term_id',
    [
        ('hermaphrodite', 'NCBITaxon:7719'),  # Ciona intestinalis
        ('hermaphrodite', 'NCBITaxon:27933'),  # Sycon ciliatum
        ('female', 'NCBITaxon:10090'),  # Mus musculus
        ('unspecified', 'NCBITaxon:10090'),
    ]
)
def test_hermaphrodite_sex_no_audit(sex, term_id):
    assert list(audit_non_human_donor_hermaphrodite_sex(_donor(sex, term_id), {})) == []


@pytest.mark.parametrize(
    'term_id',
    [
        'NCBITaxon:10090',  # Mus musculus
        'NCBITaxon:8364',  # Xenopus tropicalis
    ]
)
def test_hermaphrodite_sex_on_gonochoristic_taxa_fires_error(term_id):
    failures = list(audit_non_human_donor_hermaphrodite_sex(_donor('hermaphrodite', term_id), {}))
    assert len(failures) == 1
    assert failures[0].category == 'inconsistent sex'
    assert failures[0].__json__()['level_name'] == 'ERROR'


def test_hermaphrodite_sex_without_embedded_taxa_no_audit():
    value = _donor('hermaphrodite', 'NCBITaxon:10090')
    value['taxa'] = value['taxa']['@id']
    assert list(audit_non_human_donor_hermaphrodite_sex(value, {})) == []


def test_non_human_donor_mouse_hermaphrodite_fires_audit(testapp, indexer_testapp, other_lab, taxon_mus_musculus):
    item = {
        'lab': other_lab['@id'],
        'taxa': taxon_mus_musculus['@id'],
        'sex': 'hermaphrodite',
        'cxg_donor_id': 'lattice:test-cxg-audit-mouse-herm',
        'status': 'current',
    }
    donor = testapp.post_json('/non_human_donor', item, status=201).json['@graph'][0]
    res = indexer_testapp.get(donor['@id'] + '@@index-data')
    assert any(
        error['category'] == 'inconsistent sex'
        for error in _audit_errors(res)
    )


def test_non_human_donor_mouse_female_clean(indexer_testapp, non_human_donor):
    res = indexer_testapp.get(non_human_donor['@id'] + '@@index-data')
    assert not any(
        error['category'] == 'inconsistent sex'
        for error in _audit_errors(res)
    )
