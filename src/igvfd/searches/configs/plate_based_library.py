from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='PlateBasedLibrary'
)
def plate_based_library():
    return {
        'facets': {
            'library_construction_technology.term_id': {
                'title': 'Library Construction Technology'
            },
            'feature_types': {
                'title': 'Feature Types'
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
            'library_construction_technology': {
                'title': 'Library Construction Technology'
            },
            'feature_types': {
                'title': 'Feature Types'
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
