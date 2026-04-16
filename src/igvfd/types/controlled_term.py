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
    unique_key='controlled_term:term_id',
    properties={
        'title': 'Controlled Terms',
        'description': 'Listing of controlled vocabulary terms from biological ontologies',
    }
)
class ControlledTerm(Item):
    item_type = 'controlled_term'
    name_key = 'term_id'
    schema = load_schema('igvfd:schemas/controlled_term.json')

    @staticmethod
    def _get_ontology_string(registry, term_id, string_key):
        if term_id not in registry['ontology']:
            return ''
        return registry['ontology'][term_id].get(string_key, '')

    @staticmethod
    def _get_ontology_slims(registry, term_id, slim_key):
        if term_id not in registry['ontology']:
            return []
        key = registry['ontology'][term_id].get(slim_key, [])
        return sorted(set(
            slim for slim in key
        )) or None

    @calculated_property(
        condition='term_id',
        schema={
            'title': 'Term Name',
            'type': 'string',
            'description': 'Human readable name for the ontology term',
            'notSubmittable': True,
        }
    )
    def term_name(self, registry, term_id):
        return self._get_ontology_string(registry, term_id, 'label')

    @calculated_property(
        condition='term_id',
        schema={
            'title': 'Definition',
            'type': 'string',
            'description': 'Definition for the term that was recorded in an ontology.',
            'notSubmittable': True,
        }
    )
    def definition(self, registry, term_id):
        return self._get_ontology_string(registry, term_id, 'description')

    @calculated_property(
        condition='term_id',
        schema={
            'title': 'Synonyms',
            'type': 'array',
            'description': 'Alternative names or synonyms for this term.',
            'uniqueItems': True,
            'items': {
                'type': 'string',
            },
            'notSubmittable': True,
        }
    )
    def synonyms(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'synonyms')

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
