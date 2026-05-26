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


def audit_single_cardinality_unexpected_linked_libraries(value, system):
    '''
    [
        {
            "audit_description": "Droplet-based libraries with single cardinality are not expected to have linked libraries.",
            "audit_category": "unexpected linked libraries",
            "audit_level": "ERROR"
        }
    ]
    '''
    if value.get('library_cardinality') != 'single':
        return
    linked = value.get('linked_libraries', [])
    if not linked:
        return
    audit_message = get_audit_message(audit_single_cardinality_unexpected_linked_libraries)
    object_type = space_in_words(value['@type'][0]).capitalize()
    lib_id = value['@id']
    linked_links = ', '.join(audit_link(path_to_text(lnk), lnk) for lnk in linked)
    detail = (
        f'{object_type} {audit_link(path_to_text(lib_id), lib_id)} '
        f'has `library_cardinality` `single` but `linked_libraries` contains '
        f'{linked_links}.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


def audit_dual_cardinality_missing_linked_libraries(value, system):
    '''
    [
        {
            "audit_description": "Droplet-based libraries with dual cardinality are expected to have a linked library.",
            "audit_category": "missing linked libraries",
            "audit_level": "ERROR"
        }
    ]
    '''
    if value.get('library_cardinality') != 'dual':
        return
    if not value.get('linked_libraries'):
        audit_message = get_audit_message(audit_dual_cardinality_missing_linked_libraries)
        object_type = space_in_words(value['@type'][0]).capitalize()
        lib_id = value['@id']
        detail = (
            f'{object_type} {audit_link(path_to_text(lib_id), lib_id)} '
            f'has `library_cardinality` `dual` but is missing `linked_libraries`.'
        )
        yield AuditFailure(
            audit_message.get('audit_category', ''),
            f'{detail} {audit_message.get("audit_description", "")}',
            level=audit_message.get('audit_level', ''),
        )


def _samples_missing_hash_index(samples):
    return [
        sample for sample in samples
        if isinstance(sample, dict) and not sample.get('hash_index')
    ]


def _samples_with_hash_index(samples):
    return [
        sample for sample in samples
        if isinstance(sample, dict) and sample.get('hash_index')
    ]


def audit_plate_based_library_samples_missing_hash_index(value, system):
    '''
    [
        {
            "audit_description": "Plate-based libraries are expected to have a hash index on every linked sample.",
            "audit_category": "missing hash index",
            "audit_level": "ERROR"
        }
    ]
    '''
    missing = _samples_missing_hash_index(value.get('samples', []))
    if not missing:
        return
    audit_message = get_audit_message(audit_plate_based_library_samples_missing_hash_index)
    object_type = space_in_words(value['@type'][0]).capitalize()
    lib_id = value['@id']
    sample_links = join_obj_paths([sample['@id'] for sample in missing])
    detail = (
        f'{object_type} {audit_link(path_to_text(lib_id), lib_id)} '
        f'has linked samples missing `hash_index`: {sample_links}.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


def audit_droplet_based_library_samples_unexpected_hash_index(value, system):
    '''
    [
        {
            "audit_description": "Droplet-based libraries are not expected to have samples with a hash index.",
            "audit_category": "unexpected hash index",
            "audit_level": "ERROR"
        }
    ]
    '''
    with_hash_index = _samples_with_hash_index(value.get('samples', []))
    if not with_hash_index:
        return
    audit_message = get_audit_message(audit_droplet_based_library_samples_unexpected_hash_index)
    object_type = space_in_words(value['@type'][0]).capitalize()
    lib_id = value['@id']
    sample_links = join_obj_paths([sample['@id'] for sample in with_hash_index])
    detail = (
        f'{object_type} {audit_link(path_to_text(lib_id), lib_id)} '
        f'has linked samples with `hash_index`: {sample_links}.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


def _self_library_identifiers(value):
    identifiers = {value['@id']}
    if value.get('uuid'):
        identifiers.add(str(value['uuid']))
    for alias in value.get('aliases', []):
        identifiers.add(alias)
    return identifiers


def audit_dual_cardinality_self_linked_library(value, system):
    '''
    [
        {
            "audit_description": "Droplet-based libraries with dual cardinality are not expected to link to themselves in linked_libraries.",
            "audit_category": "self linked library",
            "audit_level": "ERROR"
        }
    ]
    '''
    if value.get('library_cardinality') != 'dual':
        return
    linked = value.get('linked_libraries', [])
    if not linked:
        return
    self_ids = _self_library_identifiers(value)
    self_links = [lnk for lnk in linked if lnk in self_ids]
    if not self_links:
        return
    audit_message = get_audit_message(audit_dual_cardinality_self_linked_library)
    object_type = space_in_words(value['@type'][0]).capitalize()
    lib_id = value['@id']
    self_link_links = ', '.join(audit_link(path_to_text(lnk), lnk) for lnk in self_links)
    detail = (
        f'{object_type} {audit_link(path_to_text(lib_id), lib_id)} '
        f'has `library_cardinality` `dual` but `linked_libraries` contains '
        f'a link to itself ({self_link_links}).'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


def audit_dual_cardinality_linked_libraries_count(value, system):
    '''
    [
        {
            "audit_description": "Droplet-based libraries with dual cardinality are expected to have exactly one linked library.",
            "audit_category": "unexpected number of linked libraries",
            "audit_level": "ERROR"
        }
    ]
    '''
    if value.get('library_cardinality') != 'dual':
        return
    linked = value.get('linked_libraries', [])
    if linked and len(linked) != 1:
        audit_message = get_audit_message(audit_dual_cardinality_linked_libraries_count)
        object_type = space_in_words(value['@type'][0]).capitalize()
        lib_id = value['@id']
        linked_links = ', '.join(audit_link(path_to_text(lnk), lnk) for lnk in linked)
        detail = (
            f'{object_type} {audit_link(path_to_text(lib_id), lib_id)} '
            f'has `library_cardinality` `dual` but `linked_libraries` contains '
            f'{len(linked)} items ({linked_links}) instead of exactly 1.'
        )
        yield AuditFailure(
            audit_message.get('audit_category', ''),
            f'{detail} {audit_message.get("audit_description", "")}',
            level=audit_message.get('audit_level', ''),
        )


function_dispatcher_droplet_based_library_object = {
    'audit_single_cardinality_unexpected_linked_libraries': audit_single_cardinality_unexpected_linked_libraries,
    'audit_dual_cardinality_missing_linked_libraries': audit_dual_cardinality_missing_linked_libraries,
    'audit_dual_cardinality_self_linked_library': audit_dual_cardinality_self_linked_library,
    'audit_dual_cardinality_linked_libraries_count': audit_dual_cardinality_linked_libraries_count,
}


@audit_checker('DropletBasedLibrary', frame='object')
def audit_droplet_based_library_object_dispatcher(value, system):
    for function_name in function_dispatcher_droplet_based_library_object:
        for failure in function_dispatcher_droplet_based_library_object[function_name](value, system):
            yield failure


function_dispatcher_plate_based_library_embedded = {
    'audit_plate_based_library_samples_missing_hash_index': audit_plate_based_library_samples_missing_hash_index,
}


@audit_checker('PlateBasedLibrary', frame='embedded')
def audit_plate_based_library_embedded_dispatcher(value, system):
    for function_name in function_dispatcher_plate_based_library_embedded:
        for failure in function_dispatcher_plate_based_library_embedded[function_name](value, system):
            yield failure


function_dispatcher_droplet_based_library_embedded = {
    'audit_droplet_based_library_samples_unexpected_hash_index': audit_droplet_based_library_samples_unexpected_hash_index,
}


@audit_checker('DropletBasedLibrary', frame='embedded')
def audit_droplet_based_library_embedded_dispatcher(value, system):
    for function_name in function_dispatcher_droplet_based_library_embedded:
        for failure in function_dispatcher_droplet_based_library_embedded[function_name](value, system):
            yield failure
