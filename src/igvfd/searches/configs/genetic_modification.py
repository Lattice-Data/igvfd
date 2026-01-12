from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='GeneticModification'
)
def genetic_modification():
    return {
        'facets': {
            'modality': {
                'title': 'Modality'
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
            'modality': {
                'title': 'Modality'
            },
            'description': {
                'title': 'Description'
            },
            'summary': {
                'title': 'Summary'
            },
            'status': {
                'title': 'Status'
            },
        }
    }
