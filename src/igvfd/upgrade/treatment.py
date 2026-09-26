from snovault.upgrader import upgrade_step

from .aliases import preserve_invalid_aliases


@upgrade_step('treatment', '1', '2')
def treatment_1_2(value, system):
    preserve_invalid_aliases(value)
