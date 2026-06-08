from snovault.upgrader import upgrade_step

# Placeholder satisfies schema pattern until submitters supply S3 ChecksumCRC64NVME.
_CRC64NVME_BASE64_PLACEHOLDER = 'AAAAAAAAAAA'


@upgrade_step('raw_matrix_file', '1', '2')
def raw_matrix_file_1_2(value, system):
    if value.get('no_file_available'):
        return
    if 'crc64nvme_base64' not in value:
        value['crc64nvme_base64'] = _CRC64NVME_BASE64_PLACEHOLDER


@upgrade_step('raw_matrix_file', '2', '3')
def raw_matrix_file_2_3(value, system):
    value.pop('md5sum', None)


_SOFTWARE_PLACEHOLDER = 'unknown'
_GENOME_ASSEMBLY_PLACEHOLDER = 'GRCh38'


@upgrade_step('raw_matrix_file', '3', '4')
def raw_matrix_file_3_4(value, system):
    if not value.get('software'):
        value['software'] = _SOFTWARE_PLACEHOLDER
    if not value.get('genome_assembly'):
        value['genome_assembly'] = _GENOME_ASSEMBLY_PLACEHOLDER
    if 'is_multiplexed' not in value:
        value['is_multiplexed'] = False
