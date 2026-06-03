from snovault import (
    collection,
    load_schema,
    calculated_property,
)
from .base import (
    Item,
)


@collection(
    name='genetic_modifications',
    properties={
        'title': 'Genetic Modifications',
        'description': 'Listing of genetic modifications applied to biological samples',
    }
)
class GeneticModification(Item):
    item_type = 'genetic_modification'
    schema = load_schema('igvfd:schemas/genetic_modification.json')

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the genetic modification.',
            'notSubmittable': True,
        }
    )
    def summary(self, strategy=None, description=None, aliases=None):
        if description:
            return description
        if strategy:
            return strategy
        if aliases:
            return aliases[0]
        return self.uuid
