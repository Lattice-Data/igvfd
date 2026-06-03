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

ALLOWED_ONTOLOGY_SOURCES = {'CHEBI', 'UniProt'}


def audit_treatment_non_chebi_uniprot_ontological_term(value, system):
    '''
    [
        {
            "audit_description": "Treatments are expected to reference a ChEBI or UniProt controlled term as the ontological term.",
            "audit_category": "invalid ontological term",
            "audit_level": "ERROR"
        }
    ]
    '''
    ontological_term = value.get('ontological_term')
    if not isinstance(ontological_term, dict):
        return
    source = ontological_term.get('ontology_source', '')
    if source in ALLOWED_ONTOLOGY_SOURCES:
        return
    audit_message = get_audit_message(audit_treatment_non_chebi_uniprot_ontological_term)
    object_type = space_in_words(value['@type'][0]).capitalize()
    treatment_id = value['@id']
    term_id = ontological_term.get('@id', '')
    detail = (
        f'{object_type} {audit_link(path_to_text(treatment_id), treatment_id)} '
        f'has `ontological_term` {audit_link(path_to_text(term_id), term_id)} '
        f'with `ontology_source` `{source}`, which is not ChEBI or UniProt.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


function_dispatcher_treatment_embedded = {
    'audit_treatment_non_chebi_uniprot_ontological_term': audit_treatment_non_chebi_uniprot_ontological_term,
}


@audit_checker('Treatment', frame='embedded')
def audit_treatment_embedded_dispatcher(value, system):
    for function_name in function_dispatcher_treatment_embedded:
        for failure in function_dispatcher_treatment_embedded[function_name](value, system):
            yield failure
