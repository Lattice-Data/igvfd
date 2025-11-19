from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='PrimaryCell'
)
def primary_cell():
    return {
        'facets': {
            'passage_number': {
                'title': 'Passage Number'
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
            'passage_number': {
                'title': 'Passage Number'
            },
            'date_obtained': {
                'title': 'Date Obtained'
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
