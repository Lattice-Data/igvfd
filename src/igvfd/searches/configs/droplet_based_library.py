from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='DropletBasedLibrary'
)
def droplet_based_library():
    return {
        'facets': {
            'chemistry_version': {
                'title': 'Chemistry Version'
            },
            'cell_barcode_length': {
                'title': 'Cell Barcode Length'
            },
            'umi_length': {
                'title': 'UMI Length'
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
            'chemistry_version': {
                'title': 'Chemistry Version'
            },
            'cell_barcode_length': {
                'title': 'Cell Barcode Length'
            },
            'umi_length': {
                'title': 'UMI Length'
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
