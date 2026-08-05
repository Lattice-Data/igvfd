from types import SimpleNamespace
from uuid import UUID

TEST_UUID = UUID('a3b4c5d6-e7f8-9012-abcd-345678901234')
OTHER_UUID = UUID('b4c5d6e7-f8a9-0123-bcde-456789012345')
GUIDES_SIGNATURE_UPGRADE_COMMENT = (
    'guides_signature was not submitted before it became required; the schema version 4 to 5 '
    'upgrade assigned a placeholder derived from this object uuid, marked by n=0. '
    'Resubmit the computed signature for this guide set.'
)


def _v4_guide_file(**overrides):
    value = {
        'schema_version': '4',
        'lab': '/labs/test/',
        'file_format': 'csv',
        'content_type': 'guide RNA sequences',
        's3_uri': 's3://bucket/path.csv',
        'crc64nvme_base64': 'AAAAAAAAAAA',
    }
    value.update(overrides)
    return value


def _upgrade_4_5(upgrader, value, uuid=TEST_UUID):
    # system is built from the upgrade kwargs, so a stub context is enough to supply a uuid.
    return upgrader.upgrade(
        'tabular_file', value, current_version='4', target_version='5',
        context=SimpleNamespace(uuid=uuid),
    )


def test_tabular_file_upgrade_1_2_adds_crc64nvme(upgrader):
    value = {
        'schema_version': '1',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'csv',
        's3_uri': 's3://bucket/path.csv',
    }
    result = upgrader.upgrade(
        'tabular_file', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['crc64nvme_base64'] == 'AAAAAAAAAAA'


def test_tabular_file_upgrade_1_2_skips_crc_when_no_file(upgrader):
    value = {
        'schema_version': '1',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'csv',
        'no_file_available': True,
    }
    result = upgrader.upgrade(
        'tabular_file', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'crc64nvme_base64' not in result


def test_tabular_file_upgrade_1_2_preserves_existing_crc(upgrader):
    value = {
        'schema_version': '1',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'csv',
        's3_uri': 's3://bucket/path.csv',
        'crc64nvme_base64': 'BBBBBBBBBBB',
    }
    result = upgrader.upgrade(
        'tabular_file', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['crc64nvme_base64'] == 'BBBBBBBBBBB'


def test_tabular_file_upgrade_2_3_removes_md5sum(upgrader):
    value = {
        'schema_version': '2',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'csv',
        's3_uri': 's3://bucket/path.csv',
        'crc64nvme_base64': 'AAAAAAAAAAA',
    }
    result = upgrader.upgrade(
        'tabular_file', value, current_version='2', target_version='3'
    )
    assert result['schema_version'] == '3'
    assert 'md5sum' not in result


def test_tabular_file_upgrade_2_3_handles_missing_md5sum(upgrader):
    value = {
        'schema_version': '2',
        'lab': '/labs/test/',
        'file_format': 'csv',
        's3_uri': 's3://bucket/path.csv',
        'crc64nvme_base64': 'AAAAAAAAAAA',
    }
    result = upgrader.upgrade(
        'tabular_file', value, current_version='2', target_version='3'
    )
    assert result['schema_version'] == '3'
    assert 'md5sum' not in result


def test_tabular_file_upgrade_3_4_adds_content_type(upgrader):
    value = {
        'schema_version': '3',
        'lab': '/labs/test/',
        'file_format': 'csv',
        's3_uri': 's3://bucket/path.csv',
        'crc64nvme_base64': 'AAAAAAAAAAA',
    }
    result = upgrader.upgrade(
        'tabular_file', value, current_version='3', target_version='4'
    )
    assert result['schema_version'] == '4'
    assert result['content_type'] == 'guide RNA sequences'


def test_tabular_file_upgrade_3_4_preserves_existing_content_type(upgrader):
    value = {
        'schema_version': '3',
        'lab': '/labs/test/',
        'file_format': 'csv',
        's3_uri': 's3://bucket/path.csv',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'content_type': 'guide RNA sequences',
    }
    result = upgrader.upgrade(
        'tabular_file', value, current_version='3', target_version='4'
    )
    assert result['schema_version'] == '4'
    assert result['content_type'] == 'guide RNA sequences'


def test_tabular_file_upgrade_4_5_adds_guides_signature(upgrader):
    result = _upgrade_4_5(upgrader, _v4_guide_file())
    assert result['schema_version'] == '5'
    assert result['guides_signature'] == f'gsig1:set:n=0:{TEST_UUID.hex}'
    assert result['submitter_comment'] == GUIDES_SIGNATURE_UPGRADE_COMMENT


def test_tabular_file_upgrade_4_5_signature_is_unique_per_uuid(upgrader):
    first = _upgrade_4_5(upgrader, _v4_guide_file(), uuid=TEST_UUID)
    second = _upgrade_4_5(upgrader, _v4_guide_file(), uuid=OTHER_UUID)
    assert first['guides_signature'] != second['guides_signature']


def test_tabular_file_upgrade_4_5_is_deterministic(upgrader):
    first = _upgrade_4_5(upgrader, _v4_guide_file())
    second = _upgrade_4_5(upgrader, _v4_guide_file())
    assert first['guides_signature'] == second['guides_signature']


def test_tabular_file_upgrade_4_5_appends_to_existing_submitter_comment(upgrader):
    existing = 'Submitted from the 2024 pilot.'
    result = _upgrade_4_5(upgrader, _v4_guide_file(submitter_comment=existing))
    assert result['submitter_comment'].startswith(existing)
    assert GUIDES_SIGNATURE_UPGRADE_COMMENT in result['submitter_comment']
    # The submitter_comment pattern rejects leading and trailing whitespace.
    assert result['submitter_comment'] == result['submitter_comment'].strip()


def test_tabular_file_upgrade_4_5_preserves_existing_guides_signature(upgrader):
    existing = 'gsig1:set:n=7:0123456789abcdef0123456789abcdef'
    result = _upgrade_4_5(upgrader, _v4_guide_file(guides_signature=existing))
    assert result['guides_signature'] == existing
    assert 'submitter_comment' not in result


def test_tabular_file_upgrade_4_5_skips_other_content_type(upgrader):
    result = _upgrade_4_5(upgrader, _v4_guide_file(content_type='some future content type'))
    assert result['schema_version'] == '5'
    assert 'guides_signature' not in result
    assert 'submitter_comment' not in result


def test_tabular_file_upgrade_4_5_falls_back_without_context(upgrader):
    result = upgrader.upgrade(
        'tabular_file', _v4_guide_file(), current_version='4', target_version='5'
    )
    assert result['guides_signature'] == f'gsig1:set:n=0:{"0" * 32}'


def test_tabular_file_upgrade_4_5_placeholder_matches_schema_pattern(upgrader):
    import re
    from snovault.schema_utils import load_schema
    from igvfd.upgrade.tabular_file import _GUIDES_SIGNATURE_PLACEHOLDER_FALLBACK
    schema = load_schema('igvfd:schemas/tabular_file.json')
    pattern = schema['properties']['guides_signature']['pattern']
    assert re.search(pattern, _GUIDES_SIGNATURE_PLACEHOLDER_FALLBACK)
    assert re.search(pattern, _upgrade_4_5(upgrader, _v4_guide_file())['guides_signature'])


def test_tabular_file_upgrade_1_5_chain(upgrader):
    value = {
        'schema_version': '1',
        'lab': '/labs/test/',
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'csv',
        's3_uri': 's3://bucket/path.csv',
    }
    result = upgrader.upgrade(
        'tabular_file', value, current_version='1', target_version='5',
        context=SimpleNamespace(uuid=TEST_UUID),
    )
    assert result['schema_version'] == '5'
    assert result['crc64nvme_base64'] == 'AAAAAAAAAAA'
    assert 'md5sum' not in result
    assert result['content_type'] == 'guide RNA sequences'
    assert result['guides_signature'] == f'gsig1:set:n=0:{TEST_UUID.hex}'
    assert result['submitter_comment'] == GUIDES_SIGNATURE_UPGRADE_COMMENT
