from snovault.upgrader import upgrade_step

from .aliases import preserve_invalid_aliases


# user had no upgrade steps before this module, so snovault's default step (see
# default_upgrades in __init__.py) took an object at any earlier version, or none,
# straight to 6. default_upgrades skips types that have steps, so keep that path.
@upgrade_step('user', '', '6')
def user_to_6(value, system):
    return


@upgrade_step('user', '6', '7')
def user_6_7(value, system):
    preserve_invalid_aliases(value)
