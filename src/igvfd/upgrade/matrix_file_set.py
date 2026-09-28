from snovault.upgrader import upgrade_step

from .aliases import preserve_invalid_aliases


@upgrade_step('matrix_file_set', '1', '2')
def matrix_file_set_1_2(value, system):
    for key in (
        'experiment_ids',
        'source_sequence_file_sets',
        'software',
        'software_version',
        'genome_assembly',
        'genome_annotation',
    ):
        value.pop(key, None)


@upgrade_step('matrix_file_set', '2', '3')
def matrix_file_set_2_3(value, system):
    preserve_invalid_aliases(value)
