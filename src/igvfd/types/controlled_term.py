from pyramid.threadlocal import get_current_request
from pyramid.traversal import find_resource
from snovault import (
    COLLECTIONS,
    collection,
    load_schema,
    calculated_property,
)
from snovault.schema_utils import VALIDATOR_REGISTRY
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
        # uniprot terms can be "anti-{term_id}" for antibodies
        term_prefix = 'anti-' if term_id.startswith('anti-') else ''
        term_to_lookup = term_id[len(term_prefix):]
        name = self._get_ontology_string(registry, term_to_lookup, 'label')
        return term_prefix + name

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
        # uniprot terms can be "anti-{term_id}" for antibodies
        term_prefix = 'anti-' if term_id.startswith('anti-') else ''
        term_to_lookup = term_id[len(term_prefix):]
        description = self._get_ontology_string(registry, term_to_lookup, 'description')
        return term_prefix + description if description else ''

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
        condition='term_id',
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'The ontology term identifier (same as term_id).',
            'notSubmittable': True,
        }
    )
    def summary(self, term_id):
        return term_id


def isAllowedTerm(value, schema):
    """Reject a ControlledTerm link whose term_id is not a key of the property's allowedTerms."""
    # Resolve the link the way linkTo does, which reports links that do not resolve to a
    # ControlledTerm, so those return no error here.
    if not isinstance(value, str):
        return None
    request = get_current_request()
    collections = request.registry[COLLECTIONS]
    try:
        term = find_resource(collections.get('ControlledTerm', request.root), value.replace(':', '%3A'))
    except KeyError:
        return None
    if not isinstance(term, ControlledTerm):
        return None
    allowed_terms = schema['allowedTerms']
    if term.upgrade_properties().get('term_id') in allowed_terms:
        return None
    allowed = ', '.join(f'{name} ({term_id})' for term_id, name in allowed_terms.items())
    return f'{value!r} is not one of the allowed terms: {allowed}.'


VALIDATOR_REGISTRY['isAllowedTerm'] = isAllowedTerm
