from snovault.upgrader import upgrade_step

from .aliases import preserve_invalid_aliases


@upgrade_step('user', '6', '7')
def user_6_7(value, system):
    preserve_invalid_aliases(value)
