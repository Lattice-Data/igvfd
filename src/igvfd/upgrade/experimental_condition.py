from snovault.upgrader import upgrade_step

from .aliases import preserve_invalid_aliases
from .notes import append_upgrade_note


# experimental_condition had no upgrade steps before this module, so snovault's default step (see
# default_upgrades in __init__.py) took an object at any earlier version, or none,
# straight to 1. default_upgrades skips types that have steps, so keep that path.
@upgrade_step('experimental_condition', '', '1')
def experimental_condition_to_1(value, system):
    return


@upgrade_step('experimental_condition', '1', '2')
def experimental_condition_1_2(value, system):
    preserve_invalid_aliases(value)


DURATION_TO_TIME_POINT = {
    'lower_bound_duration': 'lower_bound_time_point',
    'upper_bound_duration': 'upper_bound_time_point',
    'duration_units': 'time_point_units',
}


def _format_number(number):
    if float(number).is_integer():
        return str(int(number))
    return str(number)


@upgrade_step('experimental_condition', '2', '3')
def experimental_condition_2_3(value, system):
    controlled_term = value.pop('controlled_term', None)
    if controlled_term:
        value['controlled_terms'] = [controlled_term]

    for old_name, new_name in DURATION_TO_TIME_POINT.items():
        if old_name in value:
            value[new_name] = value.pop(old_name)

    condition = value.pop('condition', None)
    amount = value.pop('value', None)
    units = value.pop('units', None)
    text_value = value.pop('text_value', None)

    removed = []
    if condition:
        removed.append(f'condition={condition}')
    if amount is not None:
        removed.append(f'value={_format_number(amount)}')
    if units:
        removed.append(f'units={units}')

    if text_value and not value.get('description'):
        value['description'] = text_value
    elif text_value:
        removed.append(f'text_value={text_value}')

    # Schema 3 needs controlled_terms or description. A legacy condition with neither, such
    # as "temperature 37 celsius", keeps its meaning as the description.
    if not value.get('controlled_terms') and not value.get('description'):
        label = [condition] if condition else []
        if amount is not None and units:
            label.append(f'{_format_number(amount)} {units}')
        if label:
            value['description'] = ' '.join(label)

    if removed:
        append_upgrade_note(
            value,
            f'Legacy properties removed during schema upgrade: {", ".join(removed)}.',
        )
