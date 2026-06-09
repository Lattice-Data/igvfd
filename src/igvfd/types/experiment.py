from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from snovault.util import Path
from .base import (
    Item,
)


@collection(
    name='experiments',
    properties={
        'title': 'Experiments',
        'description': 'Listing of experiments grouping related libraries',
    }
)
class Experiment(Item):
    item_type = 'experiment'
    schema = load_schema('igvfd:schemas/experiment.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
        Path('libraries', include=['@id', '@type']),
    ]

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the experiment.',
            'notSubmittable': True,
        }
    )
    def summary(self, aliases=None, description=None):
        if aliases:
            return aliases[0]
        if description:
            return description
        return self.uuid
