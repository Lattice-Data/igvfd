from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='RawMatrixFile'
)
def raw_matrix_file():
    return {
        'facets': {
            'software': {
                'title': 'Software'
            },
            'genome_assembly': {
                'title': 'Genome Assembly'
            },
            'file_format': {
                'title': 'File Format'
            },
            'feature_keys': {
                'title': 'Feature Keys'
            },
            'feature_counts.feature_type': {
                'title': 'Feature Type'
            },
            'no_file_available': {
                'title': 'No File Available'
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
            'file_format': {
                'title': 'File Format'
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
            'feature_keys': {
                'title': 'Feature Keys'
            },
            'observation_count': {
                'title': 'Observation Count'
            },
            'feature_counts.feature_type': {
                'title': 'Feature Type'
            },
            'feature_counts.feature_count': {
                'title': 'Feature Count'
            },
            's3_uri': {
                'title': 'S3 URI'
            },
            'no_file_available': {
                'title': 'No File Available'
            },
            'file_size': {
                'title': 'File Size'
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
