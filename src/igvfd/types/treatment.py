from snovault import (
    collection,
    load_schema,
    calculated_property,
)
from snovault.util import Path
from .base import (
    Item,
)
from .experimental_condition import validate_duration_range


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
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('ontological_term', include=['@id', 'ontology_source']),
    ]

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

    def _update(self, properties, sheets=None):
        if properties is not None:
            validate_duration_range(properties)
        super(Treatment, self)._update(properties, sheets=sheets)
