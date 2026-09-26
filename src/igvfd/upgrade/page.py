from snovault.upgrader import upgrade_step

from .aliases import preserve_invalid_aliases


@upgrade_step('page', '1', '2')
def page_1_2(value, system):
    preserve_invalid_aliases(value)
