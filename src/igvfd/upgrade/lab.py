from snovault.upgrader import upgrade_step

from .aliases import preserve_invalid_aliases


# lab had no upgrade steps before this module, so snovault's default step (see
# default_upgrades in __init__.py) took an object at any earlier version, or none,
# straight to 1. default_upgrades skips types that have steps, so keep that path.
@upgrade_step('lab', '', '1')
def lab_to_1(value, system):
    return


@upgrade_step('lab', '1', '2')
def lab_1_2(value, system):
    preserve_invalid_aliases(value)
