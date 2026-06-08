def test_matrix_file_set_upgrade_1_2_removes_fields(upgrader):
    value = {
        'schema_version': '1',
        'lab': '/labs/test/',
        'experiment_ids': ['EXP-001'],
        'source_sequence_file_sets': ['/sequence-file-sets/test/'],
        'software': 'Cell Ranger',
        'software_version': '7.1.0',
        'genome_assembly': 'GRCh38',
        'genome_annotation': 'GENCODE v44',
    }
    result = upgrader.upgrade(
        'matrix_file_set', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'experiment_ids' not in result
    assert 'source_sequence_file_sets' not in result
    assert 'software' not in result
    assert 'software_version' not in result
    assert 'genome_assembly' not in result
    assert 'genome_annotation' not in result
