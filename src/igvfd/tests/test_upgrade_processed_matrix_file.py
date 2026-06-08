def test_processed_matrix_file_upgrade_1_2_adds_crc64nvme(upgrader):
    value = {
        'schema_version': '1',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'h5ad',
        's3_uri': 's3://bucket/path.h5ad',
    }
    result = upgrader.upgrade(
        'processed_matrix_file', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['crc64nvme_base64'] == 'AAAAAAAAAAA'


def test_processed_matrix_file_upgrade_1_2_skips_crc_when_no_file(upgrader):
    value = {
        'schema_version': '1',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'h5ad',
        'no_file_available': True,
    }
    result = upgrader.upgrade(
        'processed_matrix_file', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'crc64nvme_base64' not in result


def test_processed_matrix_file_upgrade_1_2_preserves_existing_crc(upgrader):
    value = {
        'schema_version': '1',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'h5ad',
        's3_uri': 's3://bucket/path.h5ad',
        'crc64nvme_base64': 'BBBBBBBBBBB',
    }
    result = upgrader.upgrade(
        'processed_matrix_file', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['crc64nvme_base64'] == 'BBBBBBBBBBB'


def test_processed_matrix_file_upgrade_2_3_removes_md5sum(upgrader):
    value = {
        'schema_version': '2',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'h5ad',
        's3_uri': 's3://bucket/path.h5ad',
        'crc64nvme_base64': 'AAAAAAAAAAA',
    }
    result = upgrader.upgrade(
        'processed_matrix_file', value, current_version='2', target_version='3'
    )
    assert result['schema_version'] == '3'
    assert 'md5sum' not in result


def test_processed_matrix_file_upgrade_2_3_handles_missing_md5sum(upgrader):
    value = {
        'schema_version': '2',
        'lab': '/labs/test/',
        'file_format': 'h5ad',
        's3_uri': 's3://bucket/path.h5ad',
        'crc64nvme_base64': 'AAAAAAAAAAA',
    }
    result = upgrader.upgrade(
        'processed_matrix_file', value, current_version='2', target_version='3'
    )
    assert result['schema_version'] == '3'
    assert 'md5sum' not in result


def test_processed_matrix_file_upgrade_3_4_sets_is_multiplexed_false_when_missing(upgrader):
    value = {
        'schema_version': '3',
        'lab': '/labs/test/',
        'file_format': 'h5ad',
        's3_uri': 's3://bucket/path.h5ad',
        'crc64nvme_base64': 'AAAAAAAAAAA',
    }
    result = upgrader.upgrade(
        'processed_matrix_file', value, current_version='3', target_version='4'
    )
    assert result['schema_version'] == '4'
    assert result['is_multiplexed'] is False


def test_processed_matrix_file_upgrade_3_4_preserves_existing_is_multiplexed(upgrader):
    value = {
        'schema_version': '3',
        'lab': '/labs/test/',
        'file_format': 'h5ad',
        's3_uri': 's3://bucket/path.h5ad',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'is_multiplexed': True,
    }
    result = upgrader.upgrade(
        'processed_matrix_file', value, current_version='3', target_version='4'
    )
    assert result['schema_version'] == '4'
    assert result['is_multiplexed'] is True
