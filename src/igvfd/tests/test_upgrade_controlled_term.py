def test_controlled_term_upgrade_1_2_removes_term_name(upgrader):
    value = {
        'schema_version': '1',
        'term_id': 'CL:0000001',
        'ontology_source': 'CL',
        'term_name': 'legacy stored label',
        'status': 'current',
    }
    result = upgrader.upgrade(
        'controlled_term', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'term_name' not in result


def test_controlled_term_upgrade_1_2_without_term_name(upgrader):
    value = {
        'schema_version': '1',
        'term_id': 'CL:0000002',
        'ontology_source': 'CL',
        'status': 'current',
    }
    result = upgrader.upgrade(
        'controlled_term', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'term_name' not in result
