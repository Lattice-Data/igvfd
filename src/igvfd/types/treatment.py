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


def _validate_treatment_duration_range(properties):
    lower = properties.get('lower_bound_duration')
    upper = properties.get('upper_bound_duration')
    if lower is not None and upper is not None and upper < lower:
        raise ValidationFailure(
            'body',
            ['upper_bound_duration'],
            'upper_bound_duration must be greater than or equal to lower_bound_duration.',
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
            _validate_treatment_duration_range(properties)
        super(Treatment, self)._update(properties, sheets=sheets)
