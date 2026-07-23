from snovault.upgrader import upgrade_step

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
