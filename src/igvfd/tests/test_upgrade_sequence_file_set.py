def test_sequence_file_set_upgrade_1_2_sets_is_pilot_order_when_cro_order_present(upgrader):
    value = {
        'schema_version': '1',
        'lab': '/labs/test/',
        'library': '/libraries/test/',
        'run_cardinality': 'single-end',
        'CRO_order': 'AN00012345',
    }
    result = upgrader.upgrade(
        'sequence_file_set', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['is_pilot_order'] is False
    assert result['CRO_order'] == 'AN00012345'


def test_sequence_file_set_upgrade_1_2_leaves_is_pilot_order_absent_without_cro_order(upgrader):
    value = {
        'schema_version': '1',
        'lab': '/labs/test/',
        'library': '/libraries/test/',
        'run_cardinality': 'single-end',
    }
    result = upgrader.upgrade(
        'sequence_file_set', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'is_pilot_order' not in result
