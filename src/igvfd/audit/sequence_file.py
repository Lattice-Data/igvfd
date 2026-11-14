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


def audit_sequence_file_multiple_sequence_file_sets(value, system):
    '''
    [
        {
            "audit_description": "Sequence files are expected to belong to only one sequence file set.",
            "audit_category": "multiple sequence file sets",
            "audit_level": "ERROR"
        }
    ]
    '''
    request = system['request']
    # sequence_file_sets already counts a set once even when it links this file
    # in two slots; reverse links ignore status, so deleted sets are dropped here.
    set_paths = [
        path for path in value.get('sequence_file_sets', [])
        if request.embed(path, '@@object?skip_calculated=true').get('status') != 'deleted'
    ]
    if len(set_paths) < 2:
        return
    audit_message = get_audit_message(audit_sequence_file_multiple_sequence_file_sets)
    object_type = space_in_words(value['@type'][0]).capitalize()
    file_id = value['@id']
    detail = (
        f'{object_type} {audit_link(path_to_text(file_id), file_id)} '
        f'is linked from sequence file sets {join_obj_paths(set_paths)}.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


function_dispatcher_sequence_file_object = {
    'audit_sequence_file_multiple_sequence_file_sets': audit_sequence_file_multiple_sequence_file_sets,
}


@audit_checker('SequenceFile', frame='object')
def audit_sequence_file_object_dispatcher(value, system):
    for function_name in function_dispatcher_sequence_file_object:
        for failure in function_dispatcher_sequence_file_object[function_name](value, system):
            yield failure
