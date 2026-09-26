from snovault.upgrader import upgrade_step

from .aliases import preserve_invalid_aliases


@upgrade_step('access_key', '1', '2')
def access_key_1_2(value, system):
    preserve_invalid_aliases(value)
