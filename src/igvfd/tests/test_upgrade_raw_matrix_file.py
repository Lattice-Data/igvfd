def test_raw_matrix_file_upgrade_1_2_adds_crc64nvme(upgrader):
    value = {
        'schema_version': '1',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'h5',
        's3_uri': 's3://bucket/path.h5',
    }
    result = upgrader.upgrade(
        'raw_matrix_file', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['crc64nvme_base64'] == 'AAAAAAAAAAA'


def test_raw_matrix_file_upgrade_1_2_skips_crc_when_no_file(upgrader):
    value = {
        'schema_version': '1',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'h5',
        'no_file_available': True,
    }
    result = upgrader.upgrade(
        'raw_matrix_file', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'crc64nvme_base64' not in result


def test_raw_matrix_file_upgrade_1_2_preserves_existing_crc(upgrader):
    value = {
        'schema_version': '1',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'h5',
        's3_uri': 's3://bucket/path.h5',
        'crc64nvme_base64': 'BBBBBBBBBBB',
    }
    result = upgrader.upgrade(
        'raw_matrix_file', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['crc64nvme_base64'] == 'BBBBBBBBBBB'


def test_raw_matrix_file_upgrade_2_3_removes_md5sum(upgrader):
    value = {
        'schema_version': '2',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'h5',
        's3_uri': 's3://bucket/path.h5',
        'crc64nvme_base64': 'AAAAAAAAAAA',
    }
    result = upgrader.upgrade(
        'raw_matrix_file', value, current_version='2', target_version='3'
    )
    assert result['schema_version'] == '3'
    assert 'md5sum' not in result


def test_raw_matrix_file_upgrade_2_3_handles_missing_md5sum(upgrader):
    value = {
        'schema_version': '2',
        'lab': '/labs/test/',
        'file_format': 'h5',
        's3_uri': 's3://bucket/path.h5',
        'crc64nvme_base64': 'AAAAAAAAAAA',
    }
    result = upgrader.upgrade(
        'raw_matrix_file', value, current_version='2', target_version='3'
    )
    assert result['schema_version'] == '3'
    assert 'md5sum' not in result


def test_raw_matrix_file_upgrade_3_4_backfills_software_and_assembly(upgrader):
    value = {
        'schema_version': '3',
        'lab': '/labs/test/',
        'file_format': 'h5',
        's3_uri': 's3://bucket/path.h5',
        'crc64nvme_base64': 'AAAAAAAAAAA',
    }
    result = upgrader.upgrade(
        'raw_matrix_file', value, current_version='3', target_version='4'
    )
    assert result['schema_version'] == '4'
    assert result['software'] == 'unknown'
    assert result['genome_assembly'] == 'GRCh38'
    assert result['is_multiplexed'] is False
    assert 'software_version' not in result


def test_raw_matrix_file_upgrade_3_4_preserves_existing_software_version(upgrader):
    value = {
        'schema_version': '3',
        'lab': '/labs/test/',
        'file_format': 'h5',
        'software': 'Cell Ranger',
        'software_version': '7.1.0',
        'genome_assembly': 'GRCm39',
    }
    result = upgrader.upgrade(
        'raw_matrix_file', value, current_version='3', target_version='4'
    )
    assert result['schema_version'] == '4'
    assert result['software'] == 'Cell Ranger'
    assert result['software_version'] == '7.1.0'
    assert result['genome_assembly'] == 'GRCm39'
    assert result['is_multiplexed'] is False


def test_raw_matrix_file_upgrade_3_4_no_software_version_when_absent(upgrader):
    value = {
        'schema_version': '3',
        'lab': '/labs/test/',
        'file_format': 'h5',
        'software': 'Cell Ranger',
        'genome_assembly': 'GRCh38',
    }
    result = upgrader.upgrade(
        'raw_matrix_file', value, current_version='3', target_version='4'
    )
    assert result['schema_version'] == '4'
    assert 'software_version' not in result
    assert result['is_multiplexed'] is False


def test_raw_matrix_file_upgrade_3_4_preserves_existing_is_multiplexed(upgrader):
    value = {
        'schema_version': '3',
        'lab': '/labs/test/',
        'file_format': 'h5',
        'software': 'Cell Ranger',
        'software_version': '7.1.0',
        'genome_assembly': 'GRCh38',
        'is_multiplexed': True,
    }
    result = upgrader.upgrade(
        'raw_matrix_file', value, current_version='3', target_version='4'
    )
    assert result['schema_version'] == '4'
    assert result['is_multiplexed'] is True
