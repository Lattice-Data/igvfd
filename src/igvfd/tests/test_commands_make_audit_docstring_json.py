import importlib
import pytest

from snovault import TYPES

import igvfd.audit

from igvfd.audit.registered_types import (
    get_types_by_audit_function,
)
from igvfd.commands.make_audit_docstring_json import (
    ALLOWED_AUDIT_LEVELS,
    EXCLUDED_MODULES,
    EXPECTED_MESSAGE_KEYS,
    get_audit_docstring_dict,
    get_audit_messages,
    get_audit_module_names,
    get_audited_types,
    validate_excluded_modules,
)

FIXTURE_MODULE = 'igvfd.tests.fixtures.audit_docstring'


def test_make_audit_docstring_json_get_audit_messages_multiple_messages():
    assert get_audit_messages(f'{FIXTURE_MODULE}.function_with_docstring', ['Biosample']) == [
        {
            'audit_description': 'audit description',
            'audit_category': 'audit category',
            'audit_level': 'ERROR',
            'audit_types': ['Biosample'],
        },
        {
            'audit_description': 'audit description 2',
            'audit_category': 'audit category 2',
            'audit_level': 'WARNING',
            'audit_types': ['Biosample'],
        },
    ]


def test_make_audit_docstring_json_get_audit_messages_key_order_does_not_matter():
    assert get_audit_messages(f'{FIXTURE_MODULE}.function_with_docstring_out_of_order', ['Treatment']) == [
        {
            'audit_level': 'WARNING',
            'audit_category': 'audit category',
            'audit_description': 'audit description',
            'audit_types': ['Treatment'],
        },
    ]


def test_make_audit_docstring_json_get_audit_messages_improper_keys():
    with pytest.raises(ValueError):
        get_audit_messages(f'{FIXTURE_MODULE}.function_with_docstring_improper_keys', ['Treatment'])


def test_make_audit_docstring_json_get_audit_messages_missing_docstring():
    with pytest.raises(ValueError):
        get_audit_messages(f'{FIXTURE_MODULE}.function_without_docstring', ['Treatment'])


def test_make_audit_docstring_json_get_audit_messages_non_json_docstring():
    with pytest.raises(ValueError):
        get_audit_messages(f'{FIXTURE_MODULE}.function_with_non_json_docstring', ['Treatment'])


def test_make_audit_docstring_json_get_audit_messages_docstring_not_a_list():
    with pytest.raises(ValueError):
        get_audit_messages(f'{FIXTURE_MODULE}.function_with_docstring_not_a_list', ['Treatment'])


def test_make_audit_docstring_json_get_audit_messages_invalid_audit_level():
    with pytest.raises(ValueError):
        get_audit_messages(f'{FIXTURE_MODULE}.function_with_invalid_audit_level', ['Treatment'])


def test_make_audit_docstring_json_excluded_modules_exist():
    validate_excluded_modules(get_audit_module_names())


def test_make_audit_docstring_json_unknown_excluded_module_raises():
    with pytest.raises(ValueError):
        validate_excluded_modules({'igvfd.audit.biosample'})


def test_make_audit_docstring_json_registered_modules_are_processed_or_excluded():
    module_names = get_audit_module_names()
    registered_modules = {
        full_name.rpartition('.')[0]
        for full_name in get_types_by_audit_function(igvfd.audit)
    }
    assert registered_modules <= module_names
    documented_modules = {
        full_name.rpartition('.')[0]
        for full_name in get_audit_docstring_dict()
    }
    assert documented_modules == registered_modules - EXCLUDED_MODULES


def test_make_audit_docstring_json_message_shape():
    expected_keys = EXPECTED_MESSAGE_KEYS | {'audit_types'}
    audit_docstring_dict = get_audit_docstring_dict()
    assert audit_docstring_dict
    for full_name, messages in audit_docstring_dict.items():
        assert isinstance(messages, list), full_name
        assert messages, full_name
        for message in messages:
            assert set(message) == expected_keys, full_name
            assert message['audit_level'] in ALLOWED_AUDIT_LEVELS, full_name
            assert message['audit_types'], full_name
            assert all(isinstance(audit_type, str) for audit_type in message['audit_types']), full_name


def test_make_audit_docstring_json_audit_types_are_registered_types(registry):
    item_types = registry[TYPES].all
    for audit_type in get_audited_types(get_audit_docstring_dict()):
        assert audit_type in item_types, audit_type


def test_make_audit_docstring_json_audit_types_render_on_audit_page(registry):
    # The audit documentation page only renders a section for a type that appears in the
    # /profiles _hierarchy under Item and that has identifying properties or child types.
    # An audit registered against any other type is silently dropped by the page.
    displayable_type_names = get_displayable_type_names(registry)
    for audit_type in get_audited_types(get_audit_docstring_dict()):
        assert audit_type in displayable_type_names, (
            f'Audit type {audit_type} does not render on the audit documentation page. '
            f'Register the audit against a type with its own schema or child types.'
        )


def test_make_audit_docstring_json_documents_every_dispatched_function():
    # Cross-check the audit registry scan against the function_dispatcher_* dicts found by
    # name, so that a change to how dispatchers delegate cannot silently drop documentation.
    dispatched_function_names = set()
    for module_name in get_audit_module_names() - EXCLUDED_MODULES:
        module = importlib.import_module(module_name)
        for attribute_name, attribute in vars(module).items():
            if attribute_name.startswith('function_dispatcher_') and isinstance(attribute, dict):
                for function in attribute.values():
                    dispatched_function_names.add(f'{function.__module__}.{function.__name__}')
    assert dispatched_function_names == set(get_audit_docstring_dict())


def get_displayable_type_names(registry):
    item_types = registry[TYPES]

    def identifying_properties(name):
        schema = getattr(item_types.all.get(name), 'schema', None) or {}
        return schema.get('identifyingProperties') or []

    def flatten(hierarchy):
        names = []
        for name, subtypes in hierarchy.items():
            # Check subtypes first: an abstract type is displayable because it has
            # children, and asking it for a schema combines every subtype schema.
            if not subtypes and not identifying_properties(name):
                continue
            names.append(name)
            names.extend(flatten(subtypes))
        return names

    return set(flatten(item_types.hierarchy['Item']))
