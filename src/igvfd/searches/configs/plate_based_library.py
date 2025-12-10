from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='PlateBasedLibrary'
)
def plate_based_library():
    return {
        'facets': {
            'kit_version': {
                'title': 'Kit Version'
            },
            'indexing_rounds': {
                'title': 'Indexing Rounds'
            },
            'lab.title': {
                'title': 'Lab'
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
            'samples': {
                'title': 'Samples'
            },
            'kit_version': {
                'title': 'Kit Version'
            },
            'indexing_rounds': {
                'title': 'Indexing Rounds'
            },
            'multiplexing_method': {
                'title': 'Multiplexing Method'
            },
            'lab': {
                'title': 'Lab'
            },
            'status': {
                'title': 'Status'
            },
            'description': {
                'title': 'Description'
            },
            'submitted_by': {
                'title': 'Submitted By'
            },
        }
    }
