from snovault.upgrader import upgrade_step

from .aliases import preserve_invalid_aliases


@upgrade_step('experimental_condition', '1', '2')
def experimental_condition_1_2(value, system):
    preserve_invalid_aliases(value)
