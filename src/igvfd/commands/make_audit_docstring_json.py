import importlib
import json
import pkgutil

from pathlib import Path

import igvfd
import igvfd.audit

from igvfd.audit.registered_types import (
    get_types_by_audit_function,
)


EXCLUDED_MODULES = {
    'igvfd.audit.item',
}

EXPECTED_MESSAGE_KEYS = {
    'audit_description',
    'audit_category',
    'audit_level',
}

# The levels the audit documentation page can render. Narrower than snovault's
# _levelNames, which also accepts DEBUG, INFO, and NOTSET.
ALLOWED_AUDIT_LEVELS = {
    'ERROR',
    'NOT_COMPLIANT',
    'WARNING',
    'INTERNAL_ACTION',
}

OUTPUT_PATH = Path(igvfd.__file__).parent / 'static' / 'doc' / 'auditdoc.json'


def get_audit_module_names():
    return {
        name
        for _importer, name, _ispkg in pkgutil.walk_packages(
            igvfd.audit.__path__,
            prefix='igvfd.audit.'
        )
    }


def validate_excluded_modules(module_names):
    unknown_modules = EXCLUDED_MODULES - module_names
    if unknown_modules:
        raise ValueError(
            f'EXCLUDED_MODULES names modules that do not exist: {sorted(unknown_modules)}.'
        )


def get_audit_messages(full_name, audit_types):
    module_name, _, function_name = full_name.rpartition('.')
    module = importlib.import_module(module_name)
    docstring = getattr(module, function_name).__doc__
    if docstring is None:
        raise ValueError(
            f'Audit function {full_name} has no docstring. Every dispatched audit is expected '
            f'to document its description, category, and level.'
        )
    try:
        messages = json.loads(docstring)
    except json.JSONDecodeError as error:
        raise ValueError(
            f'Docstring in function {full_name} is not valid JSON format: {error}.'
        ) from error
    if not isinstance(messages, list) or not messages:
        raise ValueError(
            f'Docstring in function {full_name} is expected to be a non-empty JSON list.'
        )
    documented_messages = []
    for message in messages:
        if not isinstance(message, dict) or set(message) != EXPECTED_MESSAGE_KEYS:
            raise ValueError(
                f'Audit message in {full_name} is expected to have exactly '
                f'{sorted(EXPECTED_MESSAGE_KEYS)}, got {sorted(message)}.'
            )
        audit_level = message['audit_level']
        if audit_level not in ALLOWED_AUDIT_LEVELS:
            raise ValueError(
                f'Audit message in {full_name} has audit_level {audit_level!r}, '
                f'expected one of {sorted(ALLOWED_AUDIT_LEVELS)}.'
            )
        documented_messages.append(
            {
                **message,
                'audit_types': audit_types,
            }
        )
    return documented_messages


def get_audit_docstring_dict():
    validate_excluded_modules(get_audit_module_names())
    types_by_function = get_types_by_audit_function(igvfd.audit)
    audit_docstring_dict = {}
    for full_name, audit_types in sorted(types_by_function.items()):
        module_name, _, _function_name = full_name.rpartition('.')
        if module_name in EXCLUDED_MODULES:
            continue
        audit_docstring_dict[full_name] = get_audit_messages(full_name, audit_types)
    return audit_docstring_dict


def get_audited_types(audit_docstring_dict):
    return sorted(
        {
            audit_type
            for messages in audit_docstring_dict.values()
            for message in messages
            for audit_type in message['audit_types']
        }
    )


def main():
    audit_docstring_dict = get_audit_docstring_dict()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w') as audit_json:
        json.dump(audit_docstring_dict, audit_json, sort_keys=True, indent=2)
        audit_json.write('\n')
    audited_types = get_audited_types(audit_docstring_dict)
    joined_types = ', '.join(audited_types)
    print(
        f'Wrote {len(audit_docstring_dict)} audits across {len(audited_types)} types '
        f'to {OUTPUT_PATH}: {joined_types}'
    )


if __name__ == '__main__':
    main()
