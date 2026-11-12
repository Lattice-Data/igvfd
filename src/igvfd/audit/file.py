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


# The reverse-link properties that name the file sets holding a file:
# sequence_file_sets on SequenceFile, matrix_file_sets on the matrix files.
# No file set links a TabularFile, so this audit is not registered on it.
FILE_SET_PROPERTIES = ('sequence_file_sets', 'matrix_file_sets')


def audit_file_missing_file_set(value, system):
    '''
    [
        {
            "audit_description": "Sequence and matrix files are expected to belong to at least one file set that is not deleted.",
            "audit_category": "missing file set",
            "audit_level": "ERROR"
        }
    ]
    '''
    if value.get('status') == 'deleted':
        return
    request = system['request']
    # Reverse links ignore status, so a deleted set still names this file.
    deleted_set_paths = []
    for prop in FILE_SET_PROPERTIES:
        for set_path in value.get(prop, []):
            if request.embed(set_path, '@@object?skip_calculated=true').get('status') != 'deleted':
                return
            deleted_set_paths.append(set_path)
    audit_message = get_audit_message(audit_file_missing_file_set)
    object_type = space_in_words(value['@type'][0]).capitalize()
    file_id = value['@id']
    if not deleted_set_paths:
        linkage = 'is not linked from any file set'
    elif len(deleted_set_paths) == 1:
        linkage = f'is linked only from deleted file set {join_obj_paths(deleted_set_paths)}'
    else:
        linkage = f'is linked only from deleted file sets {join_obj_paths(deleted_set_paths)}'
    detail = f'{object_type} {audit_link(path_to_text(file_id), file_id)} {linkage}.'
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


function_dispatcher_sequence_file_object = {
    'audit_file_missing_file_set': audit_file_missing_file_set,
}


@audit_checker('SequenceFile', frame='object')
def audit_sequence_file_object_dispatcher(value, system):
    for fn in function_dispatcher_sequence_file_object.values():
        yield from fn(value, system)
