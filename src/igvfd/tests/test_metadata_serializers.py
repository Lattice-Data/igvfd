import pytest

from igvfd.metadata.serializers import maybe_int
from igvfd.metadata.serializers import map_string_to_boolean_and_int
from igvfd.metadata.serializers import map_strings_to_booleans_and_ints


@pytest.mark.parametrize(
    'value, expected',
    [
        ('12000', 12000),
        ('0', 0),
        ('-5', -5),
        # int() accepts underscore digit separators; the value must parse, not
        # be mangled into '12 000' (the previous replace('_', ' ') bug).
        ('12_000', 12000),
        # Non-integer strings fall through unchanged.
        ('1.5', '1.5'),
        ('h5ad', 'h5ad'),
        ('', ''),
    ],
)
def test_maybe_int(value, expected):
    assert maybe_int(value) == expected


def test_map_string_to_boolean_and_int():
    assert map_string_to_boolean_and_int('true') is True
    assert map_string_to_boolean_and_int('false') is False
    assert map_string_to_boolean_and_int('12000') == 12000
    assert map_string_to_boolean_and_int('h5ad') == 'h5ad'


def test_map_strings_to_booleans_and_ints():
    assert map_strings_to_booleans_and_ints(['12000', 'true', 'h5ad']) == [
        12000,
        True,
        'h5ad',
    ]
