from snovault import (
    AuditFailure,
    audit_checker,
)

from .formatter import (
    audit_link,
    get_audit_message,
    join_obj_paths,
    path_to_text,
    space_in_words,
)

ALLOWED_DEVELOPMENTAL_STAGE_ONTOLOGY_SOURCES = {
    'HsapDv',
    'MmusDv',
    'FBdv',
    'WBls',
    'ZFS',
}


def audit_biosample_missing_developmental_stages(value, system):
    '''
    [
        {
            "audit_description": "Biosamples are expected to specify a developmental stage.",
            "audit_category": "missing developmental stage",
            "audit_level": "ERROR"
        }
    ]
    '''
    if value.get('developmental_stages'):
        return
    audit_message = get_audit_message(audit_biosample_missing_developmental_stages)
    object_type = space_in_words(value['@type'][0]).capitalize()
    biosample_id = value['@id']
    detail = (
        f'{object_type} {audit_link(path_to_text(biosample_id), biosample_id)} '
        f'is missing `developmental_stages`.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


def _developmental_stages_with_invalid_ontology(developmental_stages):
    return [
        stage for stage in developmental_stages
        if isinstance(stage, dict)
        and stage.get('ontology_source', '') not in ALLOWED_DEVELOPMENTAL_STAGE_ONTOLOGY_SOURCES
    ]


def audit_biosample_invalid_developmental_stages_ontology(value, system):
    '''
    [
        {
            "audit_description": "Biosamples are expected to reference a developmental-stage controlled term.",
            "audit_category": "invalid developmental stage",
            "audit_level": "ERROR"
        }
    ]
    '''
    developmental_stages = value.get('developmental_stages', [])
    if not isinstance(developmental_stages, list):
        return
    invalid = _developmental_stages_with_invalid_ontology(developmental_stages)
    if not invalid:
        return
    audit_message = get_audit_message(audit_biosample_invalid_developmental_stages_ontology)
    object_type = space_in_words(value['@type'][0]).capitalize()
    biosample_id = value['@id']
    term_links = join_obj_paths([stage['@id'] for stage in invalid])
    detail = (
        f'{object_type} {audit_link(path_to_text(biosample_id), biosample_id)} '
        f'has `developmental_stages` with invalid ontology: {term_links}.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


function_dispatcher_biosample_object = {
    'audit_biosample_missing_developmental_stages': audit_biosample_missing_developmental_stages,
}


@audit_checker('Biosample', frame='object')
def audit_biosample_object_dispatcher(value, system):
    for function_name in function_dispatcher_biosample_object:
        for failure in function_dispatcher_biosample_object[function_name](value, system):
            yield failure


function_dispatcher_biosample_embedded = {
    'audit_biosample_invalid_developmental_stages_ontology': (
        audit_biosample_invalid_developmental_stages_ontology
    ),
}


@audit_checker('Biosample', frame='embedded')
def audit_biosample_embedded_dispatcher(value, system):
    for function_name in function_dispatcher_biosample_embedded:
        for failure in function_dispatcher_biosample_embedded[function_name](value, system):
            yield failure
