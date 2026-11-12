from pyramid.traversal import traverse
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


def sequence_file_set_paths(request, file_id):
    '''Paths of the SequenceFileSets that link file_id in any slot.

    Reads the reverse links directly, because rendering the file at @@object would
    compute every calculated property, including sra_file_names, which embeds the
    set and its mates.
    '''
    # The result is unused: embedding records file_id in the matrix's embedded_uuids.
    # A set that starts linking file_id invalidates file_id, and only then does the
    # indexer re-audit this matrix. traverse records nothing. audit_item_linked_to_deleted
    # embeds the same path today, so this is an embed-cache hit, but this audit must
    # not depend on that one.
    request.embed(file_id, '@@object?skip_calculated=true')
    context = traverse(request.root, file_id)['context']
    paths = set()
    for rev_key, (rev_type, _) in getattr(context, 'rev', {}).items():
        if rev_type == 'SequenceFileSet':
            paths.update(
                request.resource_path(request.root.get_by_uuid(set_uuid))
                for set_uuid in context.get_rev_links(rev_key)
            )
    return paths


def audit_matrix_file_derived_from_incomplete_sequence_file_set(value, system):
    '''
    [
        {
            "audit_description": "Matrix files derived from files in a sequence file set are expected to be derived from every read and index file in that set, and from at least one of its CRAM files.",
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
        set_ids.update(sequence_file_set_paths(request, file_id))
    audit_message = get_audit_message(audit_matrix_file_derived_from_incomplete_sequence_file_set)
    object_type = space_in_words(value['@type'][0]).capitalize()
    obj_id = value['@id']
    for set_id in sorted(set_ids):
        # skip_calculated omits @id, which is why set_id comes from the resource path.
        file_set = request.embed(set_id, '@@object?skip_calculated=true')
        if file_set.get('status') == 'deleted':
            continue
        problems = []
        missing_reads = sorted({
            file_set[slot]
            for slot in ILLUMINA_SLOTS
            if file_set.get(slot) and file_set[slot] not in derived_from
        })
        if missing_reads:
            problems.append(f'is missing {join_obj_paths(missing_reads)}')
        # A matrix is built from the trimmed CRAM (usually) or the untrimmed one
        # (rarely), never from both, so any one CRAM in the set is enough.
        crams = sorted({file_set[slot] for slot in CRAM_SLOTS if file_set.get(slot)})
        if crams and derived_from.isdisjoint(crams):
            problems.append(f'is missing one of {join_obj_paths(crams)}')
        if not problems:
            continue
        detail = (
            f'{object_type} {audit_link(path_to_text(obj_id), obj_id)} '
            f'is derived from files in sequence file set {audit_link(path_to_text(set_id), set_id)} '
            f'but `derived_from` {" and ".join(problems)}.'
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
