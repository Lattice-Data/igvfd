from snovault.upgrader import upgrade_step


@upgrade_step('sequence_file', '1', '2')
def sequence_file_1_2(value, system):
    if value.get('no_file_available'):
        return
    if 'read_count' not in value:
        value['read_count'] = 0
