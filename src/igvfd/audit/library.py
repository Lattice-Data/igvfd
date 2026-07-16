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


def _samples_missing_multiplexing_barcodes(samples):
    return [
        sample for sample in samples
        if isinstance(sample, dict) and not sample.get('multiplexing_barcodes')
    ]


def _samples_with_multiplexing_barcodes(samples):
    return [
        sample for sample in samples
        if isinstance(sample, dict) and sample.get('multiplexing_barcodes')
    ]


def _samples_missing_rt_indexes(samples):
    return [
        sample for sample in samples
        if isinstance(sample, dict) and not sample.get('RT_indexes')
    ]


def _samples_with_rt_indexes(samples):
    return [
        sample for sample in samples
        if isinstance(sample, dict) and sample.get('RT_indexes')
    ]


NATURAL_GENETIC_VARIATION_METHOD = 'natural genetic variation'


def _library_multiplexing_method(value):
    methods = value.get('multiplexing_method') or []
    return methods[0] if methods else None


def _library_requires_sample_barcodes(value):
    method = _library_multiplexing_method(value)
    return method is not None and method != NATURAL_GENETIC_VARIATION_METHOD


def _library_forbids_sample_barcodes(value):
    method = _library_multiplexing_method(value)
    return method is None or method == NATURAL_GENETIC_VARIATION_METHOD


def audit_library_samples_missing_multiplexing_barcodes(value, system):
    '''
    [
        {
            "audit_description": "Libraries with a barcode-based multiplexing method are expected to have multiplexing barcodes on every linked sample.",
            "audit_category": "missing multiplexing barcodes",
            "audit_level": "ERROR"
        }
    ]
    '''
    if not _library_requires_sample_barcodes(value):
        return
    missing = _samples_missing_multiplexing_barcodes(value.get('samples', []))
    if not missing:
        return
    audit_message = get_audit_message(audit_library_samples_missing_multiplexing_barcodes)
    object_type = space_in_words(value['@type'][0]).capitalize()
    lib_id = value['@id']
    sample_links = join_obj_paths([sample['@id'] for sample in missing])
    detail = (
        f'{object_type} {audit_link(path_to_text(lib_id), lib_id)} '
        f'has `multiplexing_method` but linked samples missing `multiplexing_barcodes`: '
        f'{sample_links}.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


def audit_library_samples_unexpected_multiplexing_barcodes(value, system):
    '''
    [
        {
            "audit_description": "Libraries without a multiplexing method, or with natural genetic variation multiplexing, are not expected to have samples with multiplexing barcodes.",
            "audit_category": "unexpected multiplexing barcodes",
            "audit_level": "ERROR"
        }
    ]
    '''
    if not _library_forbids_sample_barcodes(value):
        return
    with_multiplexing_barcodes = _samples_with_multiplexing_barcodes(value.get('samples', []))
    if not with_multiplexing_barcodes:
        return
    audit_message = get_audit_message(audit_library_samples_unexpected_multiplexing_barcodes)
    object_type = space_in_words(value['@type'][0]).capitalize()
    lib_id = value['@id']
    sample_links = join_obj_paths([sample['@id'] for sample in with_multiplexing_barcodes])
    detail = (
        f'{object_type} {audit_link(path_to_text(lib_id), lib_id)} '
        f'has no `multiplexing_method` but linked samples with `multiplexing_barcodes`: '
        f'{sample_links}.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


def audit_plate_based_library_samples_missing_rt_indexes(value, system):
    '''
    [
        {
            "audit_description": "Plate-based libraries are expected to have RT indexes on every linked sample.",
            "audit_category": "missing RT indexes",
            "audit_level": "WARNING"
        }
    ]
    '''
    missing = _samples_missing_rt_indexes(value.get('samples', []))
    if not missing:
        return
    audit_message = get_audit_message(audit_plate_based_library_samples_missing_rt_indexes)
    object_type = space_in_words(value['@type'][0]).capitalize()
    lib_id = value['@id']
    sample_links = join_obj_paths([sample['@id'] for sample in missing])
    detail = (
        f'{object_type} {audit_link(path_to_text(lib_id), lib_id)} '
        f'has linked samples missing `RT_indexes`: {sample_links}.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


def audit_droplet_based_library_samples_unexpected_rt_indexes(value, system):
    '''
    [
        {
            "audit_description": "Droplet-based libraries are not expected to link samples that have RT indexes.",
            "audit_category": "unexpected RT indexes",
            "audit_level": "WARNING"
        }
    ]
    '''
    with_rt_indexes = _samples_with_rt_indexes(value.get('samples', []))
    if not with_rt_indexes:
        return
    audit_message = get_audit_message(audit_droplet_based_library_samples_unexpected_rt_indexes)
    object_type = space_in_words(value['@type'][0]).capitalize()
    lib_id = value['@id']
    sample_links = join_obj_paths([sample['@id'] for sample in with_rt_indexes])
    detail = (
        f'{object_type} {audit_link(path_to_text(lib_id), lib_id)} '
        f'has linked samples with `RT_indexes`: {sample_links}.'
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
    'audit_library_samples_missing_multiplexing_barcodes': audit_library_samples_missing_multiplexing_barcodes,
    'audit_library_samples_unexpected_multiplexing_barcodes': audit_library_samples_unexpected_multiplexing_barcodes,
    'audit_plate_based_library_samples_missing_rt_indexes': audit_plate_based_library_samples_missing_rt_indexes,
}


@audit_checker('PlateBasedLibrary', frame='embedded')
def audit_plate_based_library_embedded_dispatcher(value, system):
    for function_name in function_dispatcher_plate_based_library_embedded:
        for failure in function_dispatcher_plate_based_library_embedded[function_name](value, system):
            yield failure


function_dispatcher_droplet_based_library_embedded = {
    'audit_library_samples_missing_multiplexing_barcodes': audit_library_samples_missing_multiplexing_barcodes,
    'audit_library_samples_unexpected_multiplexing_barcodes': audit_library_samples_unexpected_multiplexing_barcodes,
    'audit_droplet_based_library_samples_unexpected_rt_indexes': audit_droplet_based_library_samples_unexpected_rt_indexes,
}


@audit_checker('DropletBasedLibrary', frame='embedded')
def audit_droplet_based_library_embedded_dispatcher(value, system):
    for function_name in function_dispatcher_droplet_based_library_embedded:
        for failure in function_dispatcher_droplet_based_library_embedded[function_name](value, system):
            yield failure
