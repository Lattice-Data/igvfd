from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='Source'
)
def source():
    return {
        'facets': {
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
            'title': {
                'title': 'Title'
            },
            'name': {
                'title': 'Name'
            },
            'aliases': {
                'title': 'Aliases'
            },
            'url': {
                'title': 'URL'
            },
            'status': {
                'title': 'Status'
            },
        }
    }
