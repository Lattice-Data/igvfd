from snovault.upgrader import upgrade_step


@upgrade_step('sequence_file_set', '1', '2')
def sequence_file_set_1_2(value, system):
    if 'CRO_order' in value:
        value['is_pilot_order'] = False
