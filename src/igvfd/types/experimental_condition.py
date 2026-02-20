from snovault import (
    collection,
    load_schema,
    calculated_property,
)
from .base import (
    Item,
)


@collection(
    name='experimental_conditions',
    properties={
        'title': 'Experimental Conditions',
        'description': 'Listing of experimental conditions and environmental parameters',
    }
)
class ExperimentalCondition(Item):
    item_type = 'experimental_condition'
    schema = load_schema('igvfd:schemas/experimental_condition.json')

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the experimental condition.',
            'notSubmittable': True,
        }
    )
    def summary(self, condition=None, value=None, units=None, text_value=None, description=None, aliases=None):
        if aliases:
            return aliases[0]
        if description:
            return description
        if value is not None and units:
            return f'{condition} {value} {units}'
        if text_value:
            return f'{condition}: {text_value}'
        if condition:
            return condition
        return self.uuid
