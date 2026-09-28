from snovault.upgrader import upgrade_step

from .aliases import preserve_invalid_aliases


@upgrade_step('sequence_file_set', '1', '2')
def sequence_file_set_1_2(value, system):
    if 'CRO_order' in value:
        value['is_pilot_order'] = False


@upgrade_step('sequence_file_set', '2', '3')
def sequence_file_set_2_3(value, system):
    preserve_invalid_aliases(value)
