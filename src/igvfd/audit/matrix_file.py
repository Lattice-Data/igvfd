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
from .sequence_file_set import (
    CRAM_SLOTS,
    ILLUMINA_SLOTS,
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


def audit_matrix_file_missing_md5sum(value, system):
    '''
    [
        {
            "audit_description": "Matrix files with an S3 URI are expected to specify an MD5 checksum, which GEO requires for every processed file it receives.",
            "audit_category": "missing md5sum",
            "audit_level": "ERROR"
        }
    ]
    '''
    if not value.get('s3_uri'):
        return
    if value.get('md5sum'):
        return
    audit_message = get_audit_message(audit_matrix_file_missing_md5sum)
    object_type = space_in_words(value['@type'][0]).capitalize()
    obj_id = value['@id']
    detail = (
        f'{object_type} {audit_link(path_to_text(obj_id), obj_id)} '
        f'has `s3_uri` but is missing `md5sum`.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


def audit_matrix_file_derived_from_incomplete_sequence_file_set(value, system):
    '''
    [
        {
            "audit_description": "Matrix files derived from files in a sequence file set are expected to be derived from every file in that set, including index reads.",
            "audit_category": "incomplete derived from",
            "audit_level": "ERROR"
        }
    ]
    '''
    derived_from = set(value.get('derived_from', []))
    if not derived_from:
        return
    request = system['request']
    set_ids = set()
    for file_id in derived_from:
        set_ids.update(request.embed(file_id, '@@object').get('sequence_file_sets', []))
    audit_message = get_audit_message(audit_matrix_file_derived_from_incomplete_sequence_file_set)
    object_type = space_in_words(value['@type'][0]).capitalize()
    obj_id = value['@id']
    for set_id in sorted(set_ids):
        file_set = request.embed(set_id, '@@object?skip_calculated=true')
        if file_set.get('status') == 'deleted':
            continue
        missing = sorted({
            file_set[slot]
            for slot in ILLUMINA_SLOTS + CRAM_SLOTS
            if file_set.get(slot) and file_set[slot] not in derived_from
        })
        if not missing:
            continue
        detail = (
            f'{object_type} {audit_link(path_to_text(obj_id), obj_id)} '
            f'is derived from files in sequence file set {audit_link(path_to_text(set_id), set_id)} '
            f'but `derived_from` is missing {join_obj_paths(missing)}.'
        )
        yield AuditFailure(
            audit_message.get('audit_category', ''),
            f'{detail} {audit_message.get("audit_description", "")}',
            level=audit_message.get('audit_level', ''),
        )


function_dispatcher_raw_matrix_file_object = {
    'audit_raw_matrix_file_software_without_version': audit_raw_matrix_file_software_without_version,
    'audit_matrix_file_missing_md5sum': audit_matrix_file_missing_md5sum,
    'audit_matrix_file_derived_from_incomplete_sequence_file_set': audit_matrix_file_derived_from_incomplete_sequence_file_set,
}

function_dispatcher_processed_matrix_file_object = {
    'audit_matrix_file_missing_md5sum': audit_matrix_file_missing_md5sum,
    'audit_matrix_file_derived_from_incomplete_sequence_file_set': audit_matrix_file_derived_from_incomplete_sequence_file_set,
}


@audit_checker('RawMatrixFile', frame='object')
def audit_raw_matrix_file_object_dispatcher(value, system):
    for fn in function_dispatcher_raw_matrix_file_object.values():
        yield from fn(value, system)


@audit_checker('ProcessedMatrixFile', frame='object')
def audit_processed_matrix_file_object_dispatcher(value, system):
    for fn in function_dispatcher_processed_matrix_file_object.values():
        yield from fn(value, system)
