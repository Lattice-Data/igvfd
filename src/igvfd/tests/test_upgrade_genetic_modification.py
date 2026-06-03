import pytest

from igvfd.upgrade.genetic_modification import MODALITY_TO_STRATEGY


@pytest.mark.parametrize('legacy_modality,expected_strategy', MODALITY_TO_STRATEGY.items())
def test_genetic_modification_upgrade_1_2_maps_modality(
    upgrader, legacy_modality, expected_strategy
):
    value = {
        'schema_version': '1',
        'modality': legacy_modality,
        'status': 'current',
    }
    result = upgrader.upgrade(
        'genetic_modification', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['strategy'] == expected_strategy
    assert 'modality' not in result


def test_genetic_modification_upgrade_1_2_unknown_modality_raises(upgrader):
    value = {
        'schema_version': '1',
        'modality': 'invalid_modality',
        'status': 'current',
    }
    with pytest.raises(ValueError, match='Unknown genetic_modification modality'):
        upgrader.upgrade(
            'genetic_modification', value, current_version='1', target_version='2'
        )


def test_genetic_modification_upgrade_1_2_without_modality(upgrader):
    value = {
        'schema_version': '1',
        'status': 'current',
    }
    result = upgrader.upgrade(
        'genetic_modification', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'strategy' not in result
    assert 'modality' not in result
