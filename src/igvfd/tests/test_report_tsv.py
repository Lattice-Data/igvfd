import pytest
from igvfd.report import lookup_column_value
from igvfd.report import format_row
from igvfd.report import _convert_camel_to_snake
from igvfd.report import get_host_type


def test_format_row():
    columns = ['col1', 'col2', 'col3']
    expected = b'col1\tcol2\tcol3\r\n'
    target = format_row(columns)
    assert expected == target


def test_convert_camel_to_snake_with_two_words():
    expected = 'camel_case'
    target = _convert_camel_to_snake('CamelCase')
    assert expected == target


def test_convert_camel_to_snake_with_one_words():
    expected = 'camel'
    target = _convert_camel_to_snake('Camel')
    assert expected == target


def test_batch_download_lookup_column_value(lookup_column_value_item, lookup_column_value_validate):
    for path in lookup_column_value_validate.keys():
        assert lookup_column_value_validate[path] == lookup_column_value(lookup_column_value_item, path)


def test_get_host_type():
    assert 'localhost' == get_host_type('localhost:8000')
    assert 'data' == get_host_type('api.data.lattice-data.org')
    assert 'sandbox' == get_host_type('api.sandbox.lattice-data.org')
    assert 'staging' == get_host_type('api.staging.lattice-data.org')
    assert 'igvfd-dev' == get_host_type('igvfd-dev.demo.lattice-data.org')
    assert 'igvfd-igvf-2320-improve-sample-summary' == get_host_type(
        'igvfd-igvf-2320-improve-sample-summary.demo.lattice-data.org')


def _fake_report_request(fields, schemas_by_type):
    from types import SimpleNamespace
    from snovault import TYPES
    from webob.multidict import MultiDict

    class FakeTypes(dict):
        abstract = {}

    types = FakeTypes(
        (type_name, SimpleNamespace(schema=schema))
        for type_name, schema in schemas_by_type.items()
    )
    return SimpleNamespace(
        params=MultiDict([('field', field) for field in fields]),
        registry={
            TYPES: types,
            'SEARCH_CONFIG_REPORT_CLIENT': {type_name: [] for type_name in schemas_by_type},
        },
    )


UNTITLED_PROPERTY_SCHEMA = {
    'properties': {
        'titled': {'title': 'Titled', 'type': 'string'},
        'untitled': {'type': 'array'},
    }
}


def test_list_visible_columns_for_schemas_falls_back_to_field_name_without_title():
    from igvfd.report import list_visible_columns_for_schemas
    request = _fake_report_request(['titled', 'untitled'], {'Thing': UNTITLED_PROPERTY_SCHEMA})
    columns = list_visible_columns_for_schemas(request, UNTITLED_PROPERTY_SCHEMA, [])
    assert dict(columns) == {
        'titled': {'title': 'Titled'},
        'untitled': {'title': 'untitled'},
    }


def test_get_result_columns_falls_back_to_field_name_without_title():
    from igvfd.report import get_result_columns
    request = _fake_report_request(['titled', 'untitled'], {'Thing': UNTITLED_PROPERTY_SCHEMA})
    facets = [{'field': 'type', 'terms': [{'key': 'Thing'}]}]
    columns = get_result_columns(request, facets, {})
    assert dict(columns) == {
        'titled': {'title': 'Titled'},
        'untitled': {'title': 'untitled'},
    }
