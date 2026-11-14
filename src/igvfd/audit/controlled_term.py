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


def _ontology_entry(registry, term_id):
    # uniprot terms can be "anti-{term_id}" for antibodies; the ontology holds the bare term.
    lookup = term_id[len('anti-'):] if term_id.startswith('anti-') else term_id
    ontology = registry['ontology']
    if lookup not in ontology:
        return {}
    return ontology[lookup]


def audit_controlled_term_deprecated(value, system):
    '''
    [
        {
            "audit_description": "Controlled terms are expected to reference ontology terms that are not deprecated.",
            "audit_category": "deprecated ontological term",
            "audit_level": "ERROR"
        }
    ]
    '''
    term_id = value.get('term_id')
    if not term_id:
        return
    entry = _ontology_entry(system['registry'], term_id)
    if not entry.get('deprecated'):
        return
    audit_message = get_audit_message(audit_controlled_term_deprecated)
    object_type = space_in_words(value['@type'][0]).capitalize()
    term_path = value['@id']
    label = entry.get('label', '')
    label_text = f' ({label})' if label else ''
    detail = (
        f'{object_type} {audit_link(path_to_text(term_path), term_path)} '
        f'has `term_id` `{term_id}`{label_text}, which is deprecated in its ontology.'
    )
    replaced_by = entry.get('replaced_by')
    if replaced_by:
        detail += f' The ontology replaces it with `{replaced_by}`.'
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


function_dispatcher_controlled_term_object = {
    'audit_controlled_term_deprecated': audit_controlled_term_deprecated,
}


@audit_checker('ControlledTerm', frame='object')
def audit_controlled_term_object_dispatcher(value, system):
    for function_name in function_dispatcher_controlled_term_object:
        for failure in function_dispatcher_controlled_term_object[function_name](value, system):
            yield failure
