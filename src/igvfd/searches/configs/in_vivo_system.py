from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='InVivoSystem'
)
def in_vivo_system():
    return {
        'facets': {
            'classification': {
                'title': 'Classification'
            },
            'host': {
                'title': 'Host'
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
            'sample_terms': {
                'title': 'Sample Terms'
            },
            'donors': {
                'title': 'Donors'
            },
            'classification': {
                'title': 'Classification'
            },
            'host': {
                'title': 'Host'
            },
            'intended_cell_types': {
                'title': 'Intended Cell Types'
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
