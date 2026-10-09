from snovault import (
    collection,
    load_schema,
    calculated_property,
)
from snovault.util import Path
from snovault.validation import ValidationFailure
from .base import (
    Item,
)


TREATMENT_CONDITIONS = ('chemical treatment', 'protein treatment')

# Units rendered differently from their enum value in the summary sentence.
SUMMARY_UNITS = {
    'percent': '%',
    'pH units': '',
}


def validate_duration_range(properties):
    lower = properties.get('lower_bound_duration')
    upper = properties.get('upper_bound_duration')
    if lower is not None and upper is not None and upper < lower:
        raise ValidationFailure(
            'body',
            ['upper_bound_duration'],
            'upper_bound_duration must be greater than or equal to lower_bound_duration.',
        )


def _format_number(number):
    if float(number).is_integer():
        return str(int(number))
    return str(number)


def _format_quantity(value, units):
    rendered_units = SUMMARY_UNITS.get(units, f' {units}')
    return f'{_format_number(value)}{rendered_units}'


def _format_duration(lower, upper, units):
    if lower == upper:
        unit_label = units if lower == 1 else f'{units}s'
        return f'{_format_number(lower)} {unit_label}'
    return f'{_format_number(lower)} to {_format_number(upper)} {units}s'


@collection(
    name='experimental_conditions',
    properties={
        'title': 'Experimental Conditions',
        'description': 'Listing of experimental conditions, environmental parameters, and treatments',
    }
)
class ExperimentalCondition(Item):
    item_type = 'experimental_condition'
    schema = load_schema('igvfd:schemas/experimental_condition.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('controlled_term', include=['@id', 'term_id', 'term_name', 'ontology_source']),
    ]

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A human readable sentence summarizing the experimental condition.',
            'notSubmittable': True,
        }
    )
    def summary(
        self,
        request,
        condition,
        controlled_term=None,
        value=None,
        units=None,
        text_value=None,
        lower_bound_duration=None,
        upper_bound_duration=None,
        duration_units=None,
    ):
        label = condition if condition == 'pH' else condition[0].upper() + condition[1:]
        if condition in TREATMENT_CONDITIONS:
            agent = text_value
            if controlled_term:
                term = request.embed(controlled_term, '@@object')
                agent = term.get('term_name') or term.get('term_id')
            sentence = f'{label} with {agent}'
            if value is not None and units:
                sentence += f' at {_format_quantity(value, units)}'
        elif value is not None and units:
            sentence = f'{label} {_format_quantity(value, units)}'
        elif text_value:
            sentence = f'{label}: {text_value}'
        else:
            sentence = label
        if lower_bound_duration is not None and upper_bound_duration is not None and duration_units:
            sentence += f' for {_format_duration(lower_bound_duration, upper_bound_duration, duration_units)}'
        return sentence

    def _update(self, properties, sheets=None):
        if properties is not None:
            validate_duration_range(properties)
        super(ExperimentalCondition, self)._update(properties, sheets=sheets)
