from snovault import (
    collection,
    load_schema,
    calculated_property,
)
from .base import (
    Item,
)


@collection(
    name='controlled_terms',
    properties={
        'title': 'Controlled Terms',
        'description': 'Listing of controlled vocabulary terms from biological ontologies',
    }
)
class ControlledTerm(Item):
    item_type = 'controlled_term'
    schema = load_schema('igvfd:schemas/controlled_term.json')

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the controlled term.',
            'notSubmittable': True,
        }
    )
    def summary(self, term_name=None, aliases=None):
        if term_name:
            return term_name
        if aliases:
            return aliases[0]
        return self.uuid
