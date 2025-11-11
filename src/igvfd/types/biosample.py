from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    load_schema,
)
from snovault.util import Path
from .base import (
    Item,
)


@abstract_collection(
    name='biosamples',
    properties={
        'title': 'Biosamples',
        'description': 'Abstract base class for biosamples',
    }
)
class Biosample(Item):
    """
    Abstract base class for biosamples.
    Concrete implementations are Tissue.
    """
    item_type = 'biosample'
    base_types = ['Biosample'] + Item.base_types
    schema = load_schema('igvfd:schemas/biosample.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
    ]


@collection(
    name='tissues',
    properties={
        'title': 'Tissues',
        'description': 'Listing of tissue samples',
    }
)
class Tissue(Biosample):
    item_type = 'tissue'
    schema = load_schema('igvfd:schemas/tissue.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
        Path('donors', include=['@id', 'title', 'aliases']),
        Path('sample_terms', include=['@id', 'term_name']),
    ]

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the tissue sample.',
            'notSubmittable': True,
        }
    )
    def summary(self, aliases=None, description=None):
        if aliases:
            return aliases[0]
        if description:
            return description
        return self.uuid

