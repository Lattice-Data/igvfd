from snovault.upgrader import upgrade_step
from uuid import UUID

# Placeholder satisfies schema pattern until submitters supply S3 ChecksumCRC64NVME.
_CRC64NVME_BASE64_PLACEHOLDER = 'AAAAAAAAAAA'


@upgrade_step('tabular_file', '1', '2')
def tabular_file_1_2(value, system):
    if value.get('no_file_available'):
        return
    if 'crc64nvme_base64' not in value:
        value['crc64nvme_base64'] = _CRC64NVME_BASE64_PLACEHOLDER


@upgrade_step('tabular_file', '2', '3')
def tabular_file_2_3(value, system):
    value.pop('md5sum', None)


_CONTENT_TYPE_DEFAULT = 'guide RNA sequences'


@upgrade_step('tabular_file', '3', '4')
def tabular_file_3_4(value, system):
    if 'content_type' not in value:
        value['content_type'] = _CONTENT_TYPE_DEFAULT


_GUIDES_SIGNATURE_PLACEHOLDER_PREFIX = 'gsig1:set:n=0:'
# Used only when no uuid is reachable; production callers always pass a context.
_GUIDES_SIGNATURE_PLACEHOLDER_FALLBACK = f'{_GUIDES_SIGNATURE_PLACEHOLDER_PREFIX}{"0" * 32}'
_GUIDES_SIGNATURE_UPGRADE_COMMENT = (
    'guides_signature was not submitted before it became required; the schema version 4 to 5 '
    'upgrade assigned a placeholder derived from this object uuid, marked by n=0. '
    'Resubmit the computed signature for this guide set.'
)


def _placeholder_guides_signature(value, system):
    """A per-object placeholder. n=0 marks it as not a real signature; the uuid keeps it unique."""
    identifier = getattr(system.get('context'), 'uuid', None) or value.get('uuid')
    if identifier is None:
        return _GUIDES_SIGNATURE_PLACEHOLDER_FALLBACK
    return f'{_GUIDES_SIGNATURE_PLACEHOLDER_PREFIX}{UUID(str(identifier)).hex}'


@upgrade_step('tabular_file', '4', '5')
def tabular_file_4_5(value, system):
    if value.get('content_type') != _CONTENT_TYPE_DEFAULT:
        return
    if 'guides_signature' in value:
        return
    value['guides_signature'] = _placeholder_guides_signature(value, system)
    existing_comment = value.get('submitter_comment', '').strip()
    if _GUIDES_SIGNATURE_UPGRADE_COMMENT in existing_comment:
        return
    value['submitter_comment'] = f'{existing_comment} {_GUIDES_SIGNATURE_UPGRADE_COMMENT}'.strip()
