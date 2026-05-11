import pytest

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
