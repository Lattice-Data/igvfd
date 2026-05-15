from snovault.upgrader import upgrade_step


@upgrade_step('sequence_file', '1', '2')
def sequence_file_1_2(value, system):
    if value.get('no_file_available'):
        return
    if 'read_count' not in value:
        value['read_count'] = 0


# Placeholder satisfies schema pattern until submitters supply S3 ChecksumCRC64NVME.
_CRC64NVME_BASE64_PLACEHOLDER = 'AAAAAAAAAAA'


@upgrade_step('sequence_file', '2', '3')
def sequence_file_2_3(value, system):
    if value.get('no_file_available'):
        return
    if 'crc64nvme_base64' not in value:
        value['crc64nvme_base64'] = _CRC64NVME_BASE64_PLACEHOLDER


@upgrade_step('sequence_file', '3', '4')
def sequence_file_3_4(value, system):
    value.pop('md5sum', None)
