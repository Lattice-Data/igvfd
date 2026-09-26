import re

import pytest
from snovault import TYPES

from igvfd.upgrade.aliases import ALIAS_PATTERN
from igvfd.upgrade.aliases import preserve_invalid_aliases


# Every concrete type that inherits aliases from basic_item, with the step that anchors them.
ALIAS_UPGRADES = [
    ('access_key', '1', '2'),
    ('cell_line', '4', '5'),
    ('controlled_term', '3', '4'),
    ('document', '1', '2'),
    ('droplet_based_library', '5', '6'),
    ('experimental_condition', '1', '2'),
    ('genetic_modification', '2', '3'),
    ('human_donor', '2', '3'),
    ('image', '1', '2'),
    ('lab', '1', '2'),
    ('matrix_file_set', '2', '3'),
    ('non_human_donor', '2', '3'),
    ('organoid', '4', '5'),
    ('page', '1', '2'),
    ('plate_based_library', '6', '7'),
    ('primary_cell_culture', '4', '5'),
    ('processed_matrix_file', '4', '5'),
    ('raw_matrix_file', '5', '6'),
    ('sequence_file', '4', '5'),
    ('sequence_file_set', '2', '3'),
    ('source', '1', '2'),
    ('tabular_file', '5', '6'),
    ('tissue', '4', '5'),
    ('treatment', '1', '2'),
    ('user', '6', '7'),
]

# ALIAS_PATTERN as released with the steps above.
ALIAS_PATTERN_AS_RELEASED = r"^[a-z0-9-]+:[a-zA-Z\d_$.+!*,()'-]+(?: [a-zA-Z\d_$.+!*,()'-]+)*(?![\s\S])"


@pytest.mark.parametrize(('item_type', 'current_version', 'target_version'), ALIAS_UPGRADES)
def test_upgrade_preserves_rejected_aliases_in_notes(upgrader, item_type, current_version, target_version):
    value = {
        'schema_version': current_version,
        'aliases': ['lattice:kept alias', 'lattice:dropped-alias\n'],
    }
    result = upgrader.upgrade(item_type, value, current_version=current_version, target_version=target_version)
    assert result['schema_version'] == target_version
    assert result['aliases'] == ['lattice:kept alias']
    assert result['notes'] == 'Aliases removed during schema upgrade: "lattice:dropped-alias\\n".'


def test_alias_upgrades_cover_every_type_with_aliases(registry):
    types = registry[TYPES]
    with_aliases = {
        name for name, type_info in types.by_item_type.items()
        if 'aliases' in type_info.schema['properties']
    }
    assert {item_type for item_type, _, _ in ALIAS_UPGRADES} == with_aliases
    # At least, not equal: later bumps for unrelated changes must not force editing the
    # released steps listed above.
    for item_type, _, target_version in ALIAS_UPGRADES:
        assert int(types[item_type].schema_version) >= int(target_version), item_type


def test_preserve_invalid_aliases_keeps_valid_aliases():
    value = {'aliases': ['lattice:one', 'lattice:two words'], 'notes': 'Existing note.'}
    preserve_invalid_aliases(value)
    assert value == {'aliases': ['lattice:one', 'lattice:two words'], 'notes': 'Existing note.'}


def test_preserve_invalid_aliases_without_aliases():
    value = {'notes': 'Existing note.'}
    preserve_invalid_aliases(value)
    assert value == {'notes': 'Existing note.'}


@pytest.mark.parametrize('aliases', [[], None])
def test_preserve_invalid_aliases_drops_empty_aliases(aliases):
    value = {'aliases': aliases}
    preserve_invalid_aliases(value)
    assert value == {}


def test_preserve_invalid_aliases_drops_property_when_none_survive():
    value = {'aliases': ['lattice:tab\tinside', 'lattice:non\xa0breaking'], 'notes': 'Existing note.'}
    preserve_invalid_aliases(value)
    assert 'aliases' not in value
    # Appended on its own line, with each alias JSON-quoted so its whitespace shows.
    assert value['notes'] == (
        'Existing note.\n'
        'Aliases removed during schema upgrade: "lattice:tab\\tinside", "lattice:non\\u00a0breaking".'
    )


def test_upgrade_alias_pattern_is_frozen():
    assert ALIAS_PATTERN.pattern == ALIAS_PATTERN_AS_RELEASED, (
        'The released steps must keep removing exactly what they removed on release. '
        'Add a new constant and steps rather than editing this one.'
    )


def test_upgrade_alias_pattern_agrees_with_schema(registry):
    # ALIAS_PATTERN leaves out the prefix list, so compare it with the schema on aliases
    # whose prefix the schema accepts.
    schema_pattern = re.compile(registry[TYPES]['lab'].schema['properties']['aliases']['items']['pattern'])
    for alias in [
        'will-allen:test-alias', 'will-allen:test alias', "lattice:a_$.+!*,()'-b c d",
        'will-allen:test-alias\n', 'will-allen:test-alias\n\n', 'will-allen:test alias\r\n',
        'will-allen:test\talias', 'will-allen:test\nalias', 'will-allen:test\xa0alias',
        'will-allen:test  alias', ' will-allen:test-alias', 'will-allen:test-alias ', 'will-allen:',
    ]:
        assert bool(ALIAS_PATTERN.search(alias)) == bool(schema_pattern.search(alias)), (
            f'{alias!r}: the schema aliases pattern changed how it treats whitespace. If it '
            'narrowed again, add a new constant and steps for that schema version and point '
            'this test at the new constant; ALIAS_PATTERN stays frozen for the released steps.'
        )
