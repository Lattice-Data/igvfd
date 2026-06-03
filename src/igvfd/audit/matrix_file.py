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


def audit_raw_matrix_file_software_without_version(value, system):
    '''
    [
        {
            "audit_description": "Raw matrix files with software specified are expected to also specify the software version.",
            "audit_category": "missing software version",
            "audit_level": "WARNING"
        }
    ]
    '''
    if not value.get('software'):
        return
    if value.get('software_version'):
        return
    audit_message = get_audit_message(audit_raw_matrix_file_software_without_version)
    object_type = space_in_words(value['@type'][0]).capitalize()
    obj_id = value['@id']
    detail = (
        f'{object_type} {audit_link(path_to_text(obj_id), obj_id)} '
        f'has `software` but is missing `software_version`.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


function_dispatcher_raw_matrix_file_object = {
    'audit_raw_matrix_file_software_without_version': audit_raw_matrix_file_software_without_version,
}


@audit_checker('RawMatrixFile', frame='object')
def audit_raw_matrix_file_object_dispatcher(value, system):
    for fn in function_dispatcher_raw_matrix_file_object.values():
        yield from fn(value, system)
