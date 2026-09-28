from snovault.upgrader import upgrade_step

from .aliases import preserve_invalid_aliases


# treatment had no upgrade steps before this module, so snovault's default step (see
# default_upgrades in __init__.py) took an object at any earlier version, or none,
# straight to 1. default_upgrades skips types that have steps, so keep that path.
@upgrade_step('treatment', '', '1')
def treatment_to_1(value, system):
    return


@upgrade_step('treatment', '1', '2')
def treatment_1_2(value, system):
    preserve_invalid_aliases(value)
