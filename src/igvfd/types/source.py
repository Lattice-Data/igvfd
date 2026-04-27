from snovault import (
    collection,
    load_schema,
    calculated_property,
)
from snovault.util import Path
from .base import (
    Item,
)


@collection(
    name='sources',
    unique_key='source:name',
    properties={
        'title': 'Sources',
        'description': 'Listing of vendors and labs that provide samples for study',
    }
)
class Source(Item):
    item_type = 'source'
    schema = load_schema('igvfd:schemas/source.json')
    name_key = 'name'
    embedded_with_frame = [
        Path('submitted_by', include=['@id', 'title']),
    ]

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the source.',
            'notSubmittable': True,
        }
    )
    def summary(self, title):
        return title
