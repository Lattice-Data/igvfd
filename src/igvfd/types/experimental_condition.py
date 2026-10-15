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


def validate_bound_order(properties, lower_name, upper_name):
    lower = properties.get(lower_name)
    upper = properties.get(upper_name)
    if lower is not None and upper is not None and upper < lower:
        raise ValidationFailure(
            'body',
            [upper_name],
            f'{upper_name} must be greater than or equal to {lower_name}.',
        )


def _format_number(number):
    if float(number).is_integer():
        return str(int(number))
    return str(number)


def _join_names(names):
    if len(names) < 2:
        return ''.join(names)
    return f'{", ".join(names[:-1])} and {names[-1]}'


def _format_time_point(lower, upper, units):
    if lower == upper:
        unit_label = units if lower == 1 else f'{units}s'
        return f'{_format_number(lower)} {unit_label}'
    return f'{_format_number(lower)}-{_format_number(upper)} {units}s'


@collection(
    name='experimental_conditions',
    properties={
        'title': 'Experimental Conditions',
        'description': 'Listing of experimental conditions that biological samples were exposed to',
    }
)
class ExperimentalCondition(Item):
    item_type = 'experimental_condition'
    schema = load_schema('igvfd:schemas/experimental_condition.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('controlled_terms', include=['@id', 'term_id', 'term_name', 'ontology_source']),
    ]

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'The description of the experimental condition, or else its controlled terms and time point.',
            'notSubmittable': True,
        }
    )
    def summary(
        self,
        request,
        description=None,
        controlled_terms=None,
        lower_bound_time_point=None,
        upper_bound_time_point=None,
        time_point_units=None,
    ):
        if description:
            return description
        names = []
        for term_path in controlled_terms or []:
            term = request.embed(term_path, '@@object')
            names.append(term.get('term_name') or term.get('term_id'))
        parts = [_join_names(names)]
        if lower_bound_time_point is not None and upper_bound_time_point is not None and time_point_units:
            parts.append(_format_time_point(lower_bound_time_point, upper_bound_time_point, time_point_units))
        return ', '.join(part for part in parts if part) or str(self.uuid)

    def _update(self, properties, sheets=None):
        if properties is not None:
            validate_bound_order(properties, 'lower_bound_time_point', 'upper_bound_time_point')
        super(ExperimentalCondition, self)._update(properties, sheets=sheets)
