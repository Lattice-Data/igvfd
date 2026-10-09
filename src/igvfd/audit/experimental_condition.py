from snovault import (
    AuditFailure,
    audit_checker,
)

from .formatter import (
    audit_link,
    get_audit_message,
    path_to_text,
    space_in_words,
)

EXPECTED_TREATMENT_ONTOLOGY_SOURCES = {
    'chemical treatment': 'CHEBI',
    'protein treatment': 'UniProt',
}


def audit_experimental_condition_treatment_ontology_source(value, system):
    '''
    [
        {
            "audit_description": "Chemical treatments are expected to reference a ChEBI controlled term, and protein treatments a UniProt controlled term.",
            "audit_category": "invalid ontological term",
            "audit_level": "ERROR"
        }
    ]
    '''
    expected_source = EXPECTED_TREATMENT_ONTOLOGY_SOURCES.get(value.get('condition'))
    controlled_term = value.get('controlled_term')
    if expected_source is None or not isinstance(controlled_term, dict):
        return
    source = controlled_term.get('ontology_source', '')
    if source == expected_source:
        return
    audit_message = get_audit_message(audit_experimental_condition_treatment_ontology_source)
    object_type = space_in_words(value['@type'][0]).capitalize()
    condition_id = value['@id']
    term_id = controlled_term.get('@id', '')
    detail = (
        f'{object_type} {audit_link(path_to_text(condition_id), condition_id)} '
        f'with `condition` `{value["condition"]}` '
        f'has `controlled_term` {audit_link(path_to_text(term_id), term_id)} '
        f'with `ontology_source` `{source}`, expected `{expected_source}`.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


function_dispatcher_experimental_condition_embedded = {
    'audit_experimental_condition_treatment_ontology_source': audit_experimental_condition_treatment_ontology_source,
}


@audit_checker('ExperimentalCondition', frame='embedded')
def audit_experimental_condition_embedded_dispatcher(value, system):
    for function_name in function_dispatcher_experimental_condition_embedded:
        for failure in function_dispatcher_experimental_condition_embedded[function_name](value, system):
            yield failure
