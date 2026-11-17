import re

from snovault import (
    AuditFailure,
    audit_checker,
)

from ..types.controlled_term import split_antibody_prefix
from .formatter import (
    audit_link,
    get_audit_message,
    path_to_text,
    space_in_words,
)


# Ontology `consider` values come as CURIEs (CL:0000000), OBO short forms (obo.CL_0000000)
# or PURLs (http://purl.obolibrary.org/obo/CL_0000000). Anything else (MESH paths, hgnc.5166,
# "False") is not a term we can suggest.
CONSIDER_TERM_PATTERN = re.compile(
    r'^(?:https?://purl\.obolibrary\.org/obo/|obo\.)?([A-Za-z][A-Za-z0-9]*)[_:]([A-Za-z0-9]+)$'
)


def _ontology_entry(ontology, term_id):
    """Return the ontology entry for term_id, or None when the pinned ontology does not have it."""
    _, lookup = split_antibody_prefix(term_id)
    if lookup not in ontology:
        return None
    return ontology[lookup]


def _consider_suggestions(ontology, consider):
    """Turn an ontology `consider` value into the current terms of our ontology it names, in order.

    Values that do not parse, name an ontology we do not load, or are deprecated themselves are dropped.
    """
    if isinstance(consider, str):
        consider = [consider]
    suggestions = []
    for value in consider or []:
        match = CONSIDER_TERM_PATTERN.match(value) if isinstance(value, str) else None
        if not match:
            continue
        candidate = f'{match.group(1)}:{match.group(2)}'
        if candidate in suggestions or candidate not in ontology:
            continue
        if ontology[candidate].get('deprecated'):
            continue
        suggestions.append(candidate)
    return suggestions


def _term_text(value):
    object_type = space_in_words(value['@type'][0]).capitalize()
    term_path = value['@id']
    return f'{object_type} {audit_link(path_to_text(term_path), term_path)}'


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
    ontology = system['registry']['ontology']
    entry = _ontology_entry(ontology, term_id)
    if not entry or not entry.get('deprecated'):
        return
    audit_message = get_audit_message(audit_controlled_term_deprecated)
    label = entry.get('label', '')
    label_text = f' ({label})' if label else ''
    detail = f'{_term_text(value)} has `term_id` `{term_id}`{label_text}, which is deprecated in its ontology.'
    replaced_by = entry.get('replaced_by')
    if replaced_by:
        detail += f' The ontology replaces it with `{replaced_by}`.'
    suggestions = _consider_suggestions(ontology, entry.get('consider'))
    if suggestions:
        detail += f' The ontology suggests considering {", ".join(f"`{term}`" for term in suggestions)}.'
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


def audit_controlled_term_not_in_ontology(value, system):
    '''
    [
        {
            "audit_description": "Controlled terms are expected to reference terms in the pinned ontology file, which supplies their name and definition.",
            "audit_category": "unrecognized ontological term",
            "audit_level": "WARNING"
        }
    ]
    '''
    term_id = value.get('term_id')
    if not term_id:
        return
    if _ontology_entry(system['registry']['ontology'], term_id) is not None:
        return
    audit_message = get_audit_message(audit_controlled_term_not_in_ontology)
    detail = (
        f'{_term_text(value)} has `term_id` `{term_id}`, which is not in the pinned ontology file, '
        f'so its term metadata is blank. Check whether the term is newer than the pinned ontology '
        f'version or whether the term ID is valid.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


function_dispatcher_controlled_term_object = {
    'audit_controlled_term_deprecated': audit_controlled_term_deprecated,
    'audit_controlled_term_not_in_ontology': audit_controlled_term_not_in_ontology,
}


@audit_checker('ControlledTerm', frame='object')
def audit_controlled_term_object_dispatcher(value, system):
    for function_name in function_dispatcher_controlled_term_object:
        for failure in function_dispatcher_controlled_term_object[function_name](value, system):
            yield failure
