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

EXPECTED_ONTOLOGY_SOURCES = ('CHEBI', 'UniProt', 'EFO')


def audit_experimental_condition_controlled_term_ontology_source(value, system):
    '''
    [
        {
            "audit_description": "Experimental conditions are expected to reference ChEBI, UniProt or EFO controlled terms.",
            "audit_category": "invalid ontological term",
            "audit_level": "WARNING"
        }
    ]
    '''
    audit_message = get_audit_message(audit_experimental_condition_controlled_term_ontology_source)
    object_type = space_in_words(value['@type'][0]).capitalize()
    condition_id = value['@id']
    expected = f'{", ".join(EXPECTED_ONTOLOGY_SOURCES[:-1])} or {EXPECTED_ONTOLOGY_SOURCES[-1]}'
    for controlled_term in value.get('controlled_terms', []):
        if not isinstance(controlled_term, dict):
            continue
        source = controlled_term.get('ontology_source', '')
        if source in EXPECTED_ONTOLOGY_SOURCES:
            continue
        term_id = controlled_term.get('@id', '')
        detail = (
            f'{object_type} {audit_link(path_to_text(condition_id), condition_id)} '
            f'has `controlled_terms` {audit_link(path_to_text(term_id), term_id)} '
            f'with `ontology_source` `{source}`, expected {expected}.'
        )
        yield AuditFailure(
            audit_message.get('audit_category', ''),
            f'{detail} {audit_message.get("audit_description", "")}',
            level=audit_message.get('audit_level', ''),
        )


function_dispatcher_experimental_condition_embedded = {
    'audit_experimental_condition_controlled_term_ontology_source':
        audit_experimental_condition_controlled_term_ontology_source,
}


@audit_checker('ExperimentalCondition', frame='embedded')
def audit_experimental_condition_embedded_dispatcher(value, system):
    for function_name in function_dispatcher_experimental_condition_embedded:
        for failure in function_dispatcher_experimental_condition_embedded[function_name](value, system):
            yield failure
