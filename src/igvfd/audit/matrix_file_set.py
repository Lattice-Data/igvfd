from snovault import (
    AuditFailure,
    audit_checker,
)

from igvfd.geo_file_names import geo_name_from_s3_uri

from .formatter import (
    audit_link,
    get_audit_message,
    join_obj_paths,
    path_to_text,
    space_in_words,
)


def audit_matrix_file_set_duplicate_geo_file_name(value, system):
    '''
    [
        {
            "audit_description": "Raw matrix files in a matrix file set are expected to have different GEO file names, because GEO requires the file names in a submission to be unique.",
            "audit_category": "duplicate GEO file name",
            "audit_level": "ERROR"
        }
    ]
    '''
    request = system['request']
    files_by_name = {}
    for file_id in value.get('raw_matrix_files', []):
        # geo_file_name depends on s3_uri alone, so compute it from the stored
        # properties rather than build every calculated property of each file
        matrix_file = request.embed(file_id, '@@object?skip_calculated=true')
        if matrix_file.get('status') == 'deleted' or not matrix_file.get('s3_uri'):
            continue
        name = geo_name_from_s3_uri(matrix_file['s3_uri'])
        if name is not None:
            files_by_name.setdefault(name, []).append(file_id)
    duplicated = sorted((name, file_ids) for name, file_ids in files_by_name.items() if len(file_ids) > 1)
    if not duplicated:
        return
    audit_message = get_audit_message(audit_matrix_file_set_duplicate_geo_file_name)
    object_type = space_in_words(value['@type'][0]).capitalize()
    set_id = value['@id']
    for name, file_ids in duplicated:
        detail = (
            f'{object_type} {audit_link(path_to_text(set_id), set_id)} '
            f'links raw matrix files {join_obj_paths(sorted(file_ids))} '
            f'that share `geo_file_name` `{name}`.'
        )
        yield AuditFailure(
            audit_message.get('audit_category', ''),
            f'{detail} {audit_message.get("audit_description", "")}',
            level=audit_message.get('audit_level', ''),
        )


function_dispatcher_matrix_file_set_object = {
    'audit_matrix_file_set_duplicate_geo_file_name': audit_matrix_file_set_duplicate_geo_file_name,
}


@audit_checker('MatrixFileSet', frame='object')
def audit_matrix_file_set_object_dispatcher(value, system):
    for fn in function_dispatcher_matrix_file_set_object.values():
        yield from fn(value, system)
