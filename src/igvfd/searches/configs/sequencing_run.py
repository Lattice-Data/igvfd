from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='SequencingRun'
)
def sequencing_run():
    return {
        'facets': {
            'run_cardinality': {
                'title': 'Run Cardinality'
            },
            'sequencing_platform': {
                'title': 'Sequencing Platform'
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
            'run_cardinality': {
                'title': 'Run Cardinality'
            },
            'sequencing_platform': {
                'title': 'Sequencing Platform'
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
