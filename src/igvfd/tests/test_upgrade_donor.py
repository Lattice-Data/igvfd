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


_ETHNICITY_UUID = 'f2d9b9aa-4b22-4c8a-9d9b-3a4e2b7b5c10'


def test_human_donor_upgrade_4_to_5_moves_ethnicity_to_list(upgrader):
    value = {
        'schema_version': '4',
        'lab': '/labs/mock/',
        'cxg_donor_id': 'CXG-UPGRADE-ETHNICITY',
        'ethnicity': _ETHNICITY_UUID,
    }
    result = upgrader.upgrade('human_donor', value, current_version='4', target_version='5')
    assert result['schema_version'] == '5'
    assert 'ethnicity' not in result
    assert result['ethnicities'] == [_ETHNICITY_UUID]


def test_human_donor_upgrade_4_to_5_without_ethnicity(upgrader):
    value = {
        'schema_version': '4',
        'lab': '/labs/mock/',
        'cxg_donor_id': 'CXG-UPGRADE-NO-ETHNICITY',
    }
    result = upgrader.upgrade('human_donor', value, current_version='4', target_version='5')
    assert result['schema_version'] == '5'
    assert 'ethnicity' not in result
    assert 'ethnicities' not in result


def test_human_donor_upgrade_3_to_5_links_taxa_and_lists_ethnicity(upgrader, registry, taxon_homo_sapiens):
    value = {
        'schema_version': '3',
        'lab': '/labs/mock/',
        'taxa': 'Homo sapiens',
        'cxg_donor_id': 'CXG-UPGRADE-3-TO-5',
        'ethnicity': _ETHNICITY_UUID,
    }
    result = upgrader.upgrade(
        'human_donor', value, current_version='3', target_version='5', registry=registry
    )
    assert result['schema_version'] == '5'
    assert result['taxa'] == taxon_homo_sapiens['uuid']
    assert 'ethnicity' not in result
    assert result['ethnicities'] == [_ETHNICITY_UUID]
