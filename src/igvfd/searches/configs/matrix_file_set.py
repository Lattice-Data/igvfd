from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='MatrixFileSet'
)
def matrix_file_set():
    return {
        'facets': {
            'experiment_ids': {
                'title': 'Experiment IDs'
            },
            'software': {
                'title': 'Software'
            },
            'genome_assembly': {
                'title': 'Genome Assembly'
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
            'experiment_ids': {
                'title': 'Experiment IDs'
            },
            'raw_matrix_files': {
                'title': 'Raw Matrix Files'
            },
            'processed_matrix_files': {
                'title': 'Processed Matrix Files'
            },
            'source_sequence_file_sets': {
                'title': 'Source Sequence File Sets'
            },
            'software': {
                'title': 'Software'
            },
            'software_version': {
                'title': 'Software Version'
            },
            'genome_assembly': {
                'title': 'Genome Assembly'
            },
            'genome_annotation': {
                'title': 'Genome Annotation'
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
