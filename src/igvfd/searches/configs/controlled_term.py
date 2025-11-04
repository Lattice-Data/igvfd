from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='ControlledTerm'
)
def controlled_term():
    return {
        'facets': {
            'ontology_source': {
                'title': 'Ontology Source'
            },
            'status': {
                'title': 'Status'
            },
            'audit.ERROR.category': {
                'title': 'Audit Category: Error'
            },
            'audit.NOT_COMPLIANT.category': {
                'title': 'Audit Category: Not Compliant'
            },
            'audit.WARNING.category': {
                'title': 'Audit Category: Warning'
            },
            'audit.INTERNAL_ACTION.category': {
                'title': 'Audit Category: Internal Action'
            },
        },
        'columns': {
            'uuid': {
                'title': 'UUID'
            },
            'aliases': {
                'title': 'Aliases'
            },
            'term_id': {
                'title': 'Term ID'
            },
            'term_name': {
                'title': 'Term Name'
            },
            'ontology_source': {
                'title': 'Ontology Source'
            },
            'definition': {
                'title': 'Definition'
            },
            'status': {
                'title': 'Status'
            },
        }
    }
