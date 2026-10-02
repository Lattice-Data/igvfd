import pytest

from snovault import TYPES

from igvfd.upgrade.donor import TAXA_TERM_IDS

_EXPECTED_PLACEHOLDER = 'placeholder cxg donor id'


@pytest.mark.parametrize(
    ('item_type', 'legacy'),
    [
        (
            'human_donor',
            {
                'schema_version': '1',
                'lab': '/labs/mock/',
                'taxa': 'Homo sapiens',
            },
        ),
        (
            'non_human_donor',
            {
                'schema_version': '1',
                'lab': '/labs/mock/',
                'taxa': 'Mus musculus',
            },
        ),
    ],
)
def test_donor_upgrade_1_to_2_sets_placeholder(upgrader, item_type, legacy):
    value = legacy.copy()
    result = upgrader.upgrade(
        item_type, value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['cxg_donor_id'] == _EXPECTED_PLACEHOLDER


@pytest.mark.parametrize(
    ('item_type', 'legacy_with_id'),
    [
        (
            'human_donor',
            {
                'schema_version': '1',
                'lab': '/labs/mock/',
                'taxa': 'Homo sapiens',
                'cxg_donor_id': 'CUSTOM-CXG-ID-KEEP',
            },
        ),
        (
            'non_human_donor',
            {
                'schema_version': '1',
                'lab': '/labs/mock/',
                'taxa': 'Mus musculus',
                'cxg_donor_id': 'CUSTOM-CXG-NHM-KEEP',
            },
        ),
    ],
)
def test_donor_upgrade_1_to_2_keeps_existing_cxg(upgrader, item_type, legacy_with_id):
    expected = legacy_with_id['cxg_donor_id']
    value = legacy_with_id.copy()
    result = upgrader.upgrade(
        item_type, value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['cxg_donor_id'] == expected


@pytest.mark.parametrize(
    ('item_type', 'taxa', 'taxon_fixture'),
    [
        ('human_donor', 'Homo sapiens', 'taxon_homo_sapiens'),
        ('non_human_donor', 'Mus musculus', 'taxon_mus_musculus'),
    ],
)
def test_donor_upgrade_3_to_4_links_taxa(upgrader, registry, request, item_type, taxa, taxon_fixture):
    taxon = request.getfixturevalue(taxon_fixture)
    value = {
        'schema_version': '3',
        'lab': '/labs/mock/',
        'taxa': taxa,
        'cxg_donor_id': 'CXG-UPGRADE-TAXA',
    }
    result = upgrader.upgrade(
        item_type, value, current_version='3', target_version='4', registry=registry
    )
    assert result['schema_version'] == '4'
    assert result['taxa'] == taxon['uuid']


def test_donor_upgrade_3_to_4_raises_without_term(upgrader, registry):
    value = {
        'schema_version': '3',
        'lab': '/labs/mock/',
        'taxa': 'Danio rerio',
        'cxg_donor_id': 'CXG-UPGRADE-NO-TERM',
    }
    with pytest.raises(ValueError, match='NCBITaxon:7955'):
        upgrader.upgrade(
            'non_human_donor', value, current_version='3', target_version='4', registry=registry
        )
    assert value['taxa'] == 'Danio rerio'


def test_donor_upgrade_taxa_term_ids_are_allowed_by_schema(registry):
    # Every taxa the 3 -> 4 steps link has to be one the donor schemas accept. Later schemas
    # can add species without touching TAXA_TERM_IDS, so this only checks that direction.
    allowed_terms = {}
    for item_type in ('human_donor', 'non_human_donor'):
        allowed_terms.update(registry[TYPES][item_type].schema['properties']['taxa']['allowedTerms'])
    for taxa, term_id in TAXA_TERM_IDS.items():
        assert allowed_terms.get(term_id) == taxa, (
            f'{taxa!r} upgrades to {term_id}, which the donor schemas no longer allow as {taxa!r}. '
            'A schema that drops or renames a species needs its own upgrade step; TAXA_TERM_IDS '
            'stays frozen for the released 3 -> 4 steps.'
        )
