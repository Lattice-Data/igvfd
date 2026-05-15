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


def test_sequence_file_upgrade_2_3_adds_crc64nvme(upgrader):
    value = {
        'schema_version': '2',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'fastq',
        's3_uri': 's3://bucket/path.fastq.gz',
        'read_count': 100,
    }
    result = upgrader.upgrade(
        'sequence_file', value, current_version='2', target_version='3'
    )
    assert result['schema_version'] == '3'
    assert result['crc64nvme_base64'] == 'AAAAAAAAAAA'


def test_sequence_file_upgrade_2_3_skips_crc_when_no_file(upgrader):
    value = {
        'schema_version': '2',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'fastq',
        'no_file_available': True,
    }
    result = upgrader.upgrade(
        'sequence_file', value, current_version='2', target_version='3'
    )
    assert result['schema_version'] == '3'
    assert 'crc64nvme_base64' not in result


def test_sequence_file_upgrade_2_3_preserves_existing_crc(upgrader):
    value = {
        'schema_version': '2',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'fastq',
        's3_uri': 's3://bucket/path.fastq.gz',
        'read_count': 0,
        'crc64nvme_base64': 'BBBBBBBBBBB',
    }
    result = upgrader.upgrade(
        'sequence_file', value, current_version='2', target_version='3'
    )
    assert result['schema_version'] == '3'
    assert result['crc64nvme_base64'] == 'BBBBBBBBBBB'


def test_sequence_file_upgrade_3_4_removes_md5sum(upgrader):
    value = {
        'schema_version': '3',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'fastq',
        's3_uri': 's3://bucket/path.fastq.gz',
        'read_count': 100,
        'crc64nvme_base64': 'AAAAAAAAAAA',
    }
    result = upgrader.upgrade(
        'sequence_file', value, current_version='3', target_version='4'
    )
    assert result['schema_version'] == '4'
    assert 'md5sum' not in result


def test_sequence_file_upgrade_3_4_handles_missing_md5sum(upgrader):
    value = {
        'schema_version': '3',
        'lab': '/labs/test/',
        'file_format': 'fastq',
        's3_uri': 's3://bucket/path.fastq.gz',
        'read_count': 100,
        'crc64nvme_base64': 'AAAAAAAAAAA',
    }
    result = upgrader.upgrade(
        'sequence_file', value, current_version='3', target_version='4'
    )
    assert result['schema_version'] == '4'
    assert 'md5sum' not in result
