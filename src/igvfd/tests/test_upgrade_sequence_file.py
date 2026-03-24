def test_sequence_file_upgrade_1_2_adds_read_count(upgrader):
    value = {
        'schema_version': '1',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'fastq',
        's3_uri': 's3://bucket/path.fastq.gz',
    }
    result = upgrader.upgrade(
        'sequence_file', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['read_count'] == 0


def test_sequence_file_upgrade_1_2_skips_read_count_when_no_file(upgrader):
    value = {
        'schema_version': '1',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'fastq',
        'no_file_available': True,
    }
    result = upgrader.upgrade(
        'sequence_file', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'read_count' not in result


def test_sequence_file_upgrade_1_2_preserves_existing_read_count(upgrader):
    value = {
        'schema_version': '1',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'fastq',
        's3_uri': 's3://bucket/path.fastq.gz',
        'read_count': 42,
    }
    result = upgrader.upgrade(
        'sequence_file', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['read_count'] == 42
