from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='ExperimentalCondition'
)
def experimental_condition():
    return {
        'facets': {
            'controlled_terms.term_name': {
                'title': 'Controlled Terms'
            },
            'controlled_terms.ontology_source': {
                'title': 'Ontology Source'
            },
            'time_point_units': {
                'title': 'Time Point Units'
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
            'controlled_terms.term_name': {
                'title': 'Controlled Terms'
            },
            'lower_bound_time_point': {
                'title': 'Lower Bound Time Point'
            },
            'upper_bound_time_point': {
                'title': 'Upper Bound Time Point'
            },
            'time_point_units': {
                'title': 'Time Point Units'
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
