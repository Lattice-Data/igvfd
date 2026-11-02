from ..types.base import (
    STATUS_HIERARCHY
)
from snovault import (
    AuditFailure,
    audit_checker,
)
from snovault import (
    UPGRADER,
)
from snovault.schema_utils import validate
from snovault.util import simple_path_ids
from .formatter import (
    audit_link,
    get_audit_message,
    join_obj_paths,
    path_to_text,
    space_in_words
)


@audit_checker('Item', frame='object')
def audit_item_schema(value, system):
    context = system['context']
    registry = system['registry']
    if not context.schema:
        return

    properties = context.properties.copy()
    current_version = properties.get('schema_version', '')
    target_version = context.type_info.schema_version
    if target_version is not None and current_version != target_version:
        upgrader = registry[UPGRADER]
        try:
            properties = upgrader.upgrade(
                context.type_info.name, properties, current_version, target_version,
                finalize=False, context=context, registry=registry)
        except RuntimeError:
            raise
        except Exception as e:
            detail = '%r upgrading from %r to %r' % (
                e, current_version, target_version)
            yield AuditFailure('upgrade failure', detail, level='INTERNAL_ACTION')
            return

        properties['schema_version'] = target_version

    properties['uuid'] = str(context.uuid)
    validated, errors = validate(context.schema, properties, properties)
    for error in errors:
        category = 'validation error'
        path = list(error.path)
        if path:
            category += ': ' + '/'.join(str(elem) for elem in path)
        detail = ('{} {} has schema error {}.'.format(
            space_in_words(value['@type'][0]).capitalize(),
            audit_link(path_to_text(value['@id']), value['@id']),
            error.message
        )
        )
        yield AuditFailure(category, detail, level='INTERNAL_ACTION')


@audit_checker('Item', frame='object')
def audit_item_linked_to_deleted(value, system):
    '''
    [
        {
            "audit_description": "Objects that are not deleted are expected to be disconnected from deleted objects.",
            "audit_category": "linked to deleted object",
            "audit_level": "ERROR"
        }
    ]
    '''
    if value.get('status') == 'deleted':
        return
    context = system['context']
    request = system['request']
    audit_message = get_audit_message(audit_item_linked_to_deleted)
    object_type = space_in_words(value['@type'][0]).capitalize()
    item_id = value['@id']
    for link_path in context.type_info.schema_links:
        deleted_paths = sorted({
            linked_id
            for linked_id in simple_path_ids(value, link_path)
            if request.embed(linked_id, '@@object?skip_calculated=true').get('status') == 'deleted'
        })
        if not deleted_paths:
            continue
        detail = (
            f'{object_type} {audit_link(path_to_text(item_id), item_id)} '
            f'links in `{link_path}` to deleted {join_obj_paths(deleted_paths)}.'
        )
        yield AuditFailure(
            audit_message.get('audit_category', ''),
            f'{detail} {audit_message.get("audit_description", "")}',
            level=audit_message.get('audit_level', ''),
        )
