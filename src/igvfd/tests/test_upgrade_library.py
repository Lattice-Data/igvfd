import pytest

from igvfd.upgrade.library import (
    DROPLET_REMOVED_PROPERTIES,
    MULTIPLEXING_METHOD_MAP,
    PLATE_REMOVED_PROPERTIES,
)

MULTIPLEXED_SAMPLES = ['sample-a', 'sample-b']
SINGLE_SAMPLE = ['sample-a']


@pytest.mark.parametrize('legacy_method,expected_method', MULTIPLEXING_METHOD_MAP.items())
def test_droplet_based_library_upgrade_1_2_maps_multiplexing_method(
    upgrader, legacy_method, expected_method
):
    value = {
        'schema_version': '1',
        'samples': MULTIPLEXED_SAMPLES,
        'multiplexing_method': legacy_method,
        'chemistry_version': "3' v3",
        'cell_barcode_length': 16,
        'umi_length': 12,
        'status': 'current',
    }
    result = upgrader.upgrade(
        'droplet_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['multiplexing_method'] == [expected_method]
    for prop in DROPLET_REMOVED_PROPERTIES:
        assert prop not in result


def test_droplet_based_library_upgrade_1_2_without_multiplexing_method(upgrader):
    value = {
        'schema_version': '1',
        'chemistry_version': "3' v3",
        'status': 'current',
    }
    result = upgrader.upgrade(
        'droplet_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'multiplexing_method' not in result
    assert 'chemistry_version' not in result


def test_droplet_based_library_upgrade_1_2_drops_multiplexing_method_with_one_sample(upgrader):
    value = {
        'schema_version': '1',
        'samples': SINGLE_SAMPLE,
        'multiplexing_method': 'cell hashing',
        'chemistry_version': "3' v3",
        'status': 'current',
    }
    result = upgrader.upgrade(
        'droplet_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'multiplexing_method' not in result


def test_droplet_based_library_upgrade_1_2_unknown_multiplexing_method_dropped_with_one_sample(
    upgrader,
):
    value = {
        'schema_version': '1',
        'samples': SINGLE_SAMPLE,
        'multiplexing_method': 'invalid method',
        'status': 'current',
    }
    result = upgrader.upgrade(
        'droplet_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'multiplexing_method' not in result


def test_droplet_based_library_upgrade_1_2_unknown_multiplexing_method_raises(upgrader):
    value = {
        'schema_version': '1',
        'samples': MULTIPLEXED_SAMPLES,
        'multiplexing_method': 'invalid method',
        'status': 'current',
    }
    with pytest.raises(ValueError, match='Unknown multiplexing_method'):
        upgrader.upgrade(
            'droplet_based_library', value, current_version='1', target_version='2'
        )


def test_droplet_based_library_upgrade_1_2_preserves_list_multiplexing_method_with_two_samples(
    upgrader,
):
    value = {
        'schema_version': '1',
        'samples': MULTIPLEXED_SAMPLES,
        'multiplexing_method': ['antibody hashing'],
        'status': 'current',
    }
    result = upgrader.upgrade(
        'droplet_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['multiplexing_method'] == ['antibody hashing']


@pytest.mark.parametrize('legacy_method,expected_method', MULTIPLEXING_METHOD_MAP.items())
def test_plate_based_library_upgrade_1_2_maps_multiplexing_method(
    upgrader, legacy_method, expected_method
):
    value = {
        'schema_version': '1',
        'samples': MULTIPLEXED_SAMPLES,
        'multiplexing_method': legacy_method,
        'kit_version': 'sci-RNA-seq3',
        'indexing_rounds': 3,
        'status': 'current',
    }
    result = upgrader.upgrade(
        'plate_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['multiplexing_method'] == [expected_method]
    for prop in PLATE_REMOVED_PROPERTIES:
        assert prop not in result


def test_plate_based_library_upgrade_1_2_without_multiplexing_method(upgrader):
    value = {
        'schema_version': '1',
        'kit_version': 'QuantumScale Single Cell RNA',
        'indexing_rounds': 4,
        'status': 'current',
    }
    result = upgrader.upgrade(
        'plate_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'multiplexing_method' not in result
    assert 'kit_version' not in result
    assert 'indexing_rounds' not in result


def test_plate_based_library_upgrade_1_2_drops_multiplexing_method_with_one_sample(upgrader):
    value = {
        'schema_version': '1',
        'samples': SINGLE_SAMPLE,
        'multiplexing_method': 'cell hashing',
        'kit_version': 'sci-RNA-seq3',
        'status': 'current',
    }
    result = upgrader.upgrade(
        'plate_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'multiplexing_method' not in result


def test_plate_based_library_upgrade_1_2_preserves_list_multiplexing_method_with_two_samples(
    upgrader,
):
    value = {
        'schema_version': '1',
        'samples': MULTIPLEXED_SAMPLES,
        'multiplexing_method': ['combinatorial indexing'],
        'status': 'current',
    }
    result = upgrader.upgrade(
        'plate_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['multiplexing_method'] == ['combinatorial indexing']


def test_plate_based_library_upgrade_2_3_defaults_library_cardinality_single(upgrader):
    value = {
        'schema_version': '2',
        'status': 'current',
    }
    result = upgrader.upgrade(
        'plate_based_library', value, current_version='2', target_version='3'
    )
    assert result['schema_version'] == '3'
    assert result['library_cardinality'] == 'single'


def test_plate_based_library_upgrade_2_3_preserves_library_cardinality_dual(upgrader):
    value = {
        'schema_version': '2',
        'library_cardinality': 'dual',
        'status': 'current',
    }
    result = upgrader.upgrade(
        'plate_based_library', value, current_version='2', target_version='3'
    )
    assert result['schema_version'] == '3'
    assert result['library_cardinality'] == 'dual'
