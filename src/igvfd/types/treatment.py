from snovault import (
    collection,
    load_schema,
    calculated_property,
)
from .base import (
    Item,
)


@collection(
    name='treatments',
    properties={
        'title': 'Treatments',
        'description': 'Listing of treatments applied to biological samples (ChEBI/UniProt agents)',
    }
)
class Treatment(Item):
    item_type = 'treatment'
    schema = load_schema('igvfd:schemas/treatment.json')

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the treatment.',
            'notSubmittable': True,
        }
    )
    def summary(self, description=None, aliases=None):
        if aliases:
            return aliases[0]
        if description:
            return description
        return self.uuid
