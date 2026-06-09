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


def _library_is_droplet_based(library):
    return isinstance(library, dict) and 'DropletBasedLibrary' in library.get('@type', [])


def _library_is_plate_based(library):
    return isinstance(library, dict) and 'PlateBasedLibrary' in library.get('@type', [])


def audit_experiment_mixed_library_types(value, system):
    '''
    [
        {
            "audit_description": "Experiments are expected to group libraries of a single preparation type (all droplet-based or all plate-based).",
            "audit_category": "inconsistent library types",
            "audit_level": "ERROR"
        }
    ]
    '''
    libraries = value.get('libraries', [])
    if not libraries:
        return
    has_droplet = any(_library_is_droplet_based(library) for library in libraries)
    has_plate = any(_library_is_plate_based(library) for library in libraries)
    if not (has_droplet and has_plate):
        return
    audit_message = get_audit_message(audit_experiment_mixed_library_types)
    object_type = space_in_words(value['@type'][0]).capitalize()
    experiment_id = value['@id']
    library_links = ', '.join(
        audit_link(path_to_text(library['@id']), library['@id'])
        for library in libraries
        if isinstance(library, dict) and library.get('@id')
    )
    detail = (
        f'{object_type} {audit_link(path_to_text(experiment_id), experiment_id)} '
        f'groups both droplet-based and plate-based libraries: {library_links}.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


function_dispatcher_experiment_embedded = {
    'audit_experiment_mixed_library_types': audit_experiment_mixed_library_types,
}


@audit_checker('Experiment', frame='embedded')
def audit_experiment_embedded_dispatcher(value, system):
    for function_name in function_dispatcher_experiment_embedded:
        for failure in function_dispatcher_experiment_embedded[function_name](value, system):
            yield failure
