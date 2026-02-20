from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='ExperimentalCondition'
)
def experimental_condition():
    return {
        'facets': {
            'condition': {
                'title': 'Condition'
            },
            'units': {
                'title': 'Units'
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
            'condition': {
                'title': 'Condition'
            },
            'value': {
                'title': 'Value'
            },
            'units': {
                'title': 'Units'
            },
            'text_value': {
                'title': 'Text Value'
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
