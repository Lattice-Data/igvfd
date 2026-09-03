import re

import pytest

from igvfd.upgrade.library import (
    DROPLET_REMOVED_PROPERTIES,
    MULTIPLEXING_METHOD_MAP,
    PLATE_REMOVED_PROPERTIES,
)

# Distinguishes an absent dbxrefs key from an explicit null.
ABSENT = object()

MULTIPLEXED_SAMPLES = ['sample-a', 'sample-b']
SINGLE_SAMPLE = ['sample-a']


@pytest.mark.parametrize('legacy_method,expected_method', MULTIPLEXING_METHOD_MAP.items())
def test_droplet_based_library_upgrade_1_2_maps_multiplexing_method(
    upgrader, legacy_method, expected_method
):
    value = {
        'schema_version': '1',
        'samples': MULTIPLEXED_SAMPLES,
        'multiplexing_method': legacy_method,
        'chemistry_version': "3' v3",
        'cell_barcode_length': 16,
        'umi_length': 12,
        'status': 'current',
    }
    result = upgrader.upgrade(
        'droplet_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['multiplexing_method'] == [expected_method]
    for prop in DROPLET_REMOVED_PROPERTIES:
        assert prop not in result


def test_droplet_based_library_upgrade_1_2_without_multiplexing_method(upgrader):
    value = {
        'schema_version': '1',
        'chemistry_version': "3' v3",
        'status': 'current',
    }
    result = upgrader.upgrade(
        'droplet_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'multiplexing_method' not in result
    assert 'chemistry_version' not in result


def test_droplet_based_library_upgrade_1_2_drops_multiplexing_method_with_one_sample(upgrader):
    value = {
        'schema_version': '1',
        'samples': SINGLE_SAMPLE,
        'multiplexing_method': 'cell hashing',
        'chemistry_version': "3' v3",
        'status': 'current',
    }
    result = upgrader.upgrade(
        'droplet_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'multiplexing_method' not in result


def test_droplet_based_library_upgrade_1_2_unknown_multiplexing_method_dropped_with_one_sample(
    upgrader,
):
    value = {
        'schema_version': '1',
        'samples': SINGLE_SAMPLE,
        'multiplexing_method': 'invalid method',
        'status': 'current',
    }
    result = upgrader.upgrade(
        'droplet_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'multiplexing_method' not in result


def test_droplet_based_library_upgrade_1_2_unknown_multiplexing_method_raises(upgrader):
    value = {
        'schema_version': '1',
        'samples': MULTIPLEXED_SAMPLES,
        'multiplexing_method': 'invalid method',
        'status': 'current',
    }
    with pytest.raises(ValueError, match='Unknown multiplexing_method'):
        upgrader.upgrade(
            'droplet_based_library', value, current_version='1', target_version='2'
        )


def test_droplet_based_library_upgrade_1_2_preserves_list_multiplexing_method_with_two_samples(
    upgrader,
):
    value = {
        'schema_version': '1',
        'samples': MULTIPLEXED_SAMPLES,
        'multiplexing_method': ['antibody hashing'],
        'status': 'current',
    }
    result = upgrader.upgrade(
        'droplet_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['multiplexing_method'] == ['antibody hashing']


@pytest.mark.parametrize('legacy_method,expected_method', MULTIPLEXING_METHOD_MAP.items())
def test_plate_based_library_upgrade_1_2_maps_multiplexing_method(
    upgrader, legacy_method, expected_method
):
    value = {
        'schema_version': '1',
        'samples': MULTIPLEXED_SAMPLES,
        'multiplexing_method': legacy_method,
        'kit_version': 'sci-RNA-seq3',
        'indexing_rounds': 3,
        'status': 'current',
    }
    result = upgrader.upgrade(
        'plate_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['multiplexing_method'] == [expected_method]
    for prop in PLATE_REMOVED_PROPERTIES:
        assert prop not in result


def test_plate_based_library_upgrade_1_2_without_multiplexing_method(upgrader):
    value = {
        'schema_version': '1',
        'kit_version': 'QuantumScale Single Cell RNA',
        'indexing_rounds': 4,
        'status': 'current',
    }
    result = upgrader.upgrade(
        'plate_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'multiplexing_method' not in result
    assert 'kit_version' not in result
    assert 'indexing_rounds' not in result


def test_plate_based_library_upgrade_1_2_drops_multiplexing_method_with_one_sample(upgrader):
    value = {
        'schema_version': '1',
        'samples': SINGLE_SAMPLE,
        'multiplexing_method': 'cell hashing',
        'kit_version': 'sci-RNA-seq3',
        'status': 'current',
    }
    result = upgrader.upgrade(
        'plate_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'multiplexing_method' not in result


def test_plate_based_library_upgrade_1_2_preserves_list_multiplexing_method_with_two_samples(
    upgrader,
):
    value = {
        'schema_version': '1',
        'samples': MULTIPLEXED_SAMPLES,
        'multiplexing_method': ['combinatorial indexing'],
        'status': 'current',
    }
    result = upgrader.upgrade(
        'plate_based_library', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert result['multiplexing_method'] == ['combinatorial indexing']


def test_plate_based_library_upgrade_2_3_defaults_library_cardinality_single(upgrader):
    value = {
        'schema_version': '2',
        'status': 'current',
    }
    result = upgrader.upgrade(
        'plate_based_library', value, current_version='2', target_version='3'
    )
    assert result['schema_version'] == '3'
    assert result['library_cardinality'] == 'single'


def test_plate_based_library_upgrade_2_3_preserves_library_cardinality_dual(upgrader):
    value = {
        'schema_version': '2',
        'library_cardinality': 'dual',
        'status': 'current',
    }
    result = upgrader.upgrade(
        'plate_based_library', value, current_version='2', target_version='3'
    )
    assert result['schema_version'] == '3'
    assert result['library_cardinality'] == 'dual'


def test_droplet_based_library_upgrade_2_3_defaults_feature_types(upgrader):
    value = {
        'schema_version': '2',
        'status': 'current',
    }
    result = upgrader.upgrade(
        'droplet_based_library', value, current_version='2', target_version='3'
    )
    assert result['schema_version'] == '3'
    assert result['feature_types'] == ['Gene Expression']


def test_droplet_based_library_upgrade_2_3_preserves_feature_types(upgrader):
    value = {
        'schema_version': '2',
        'feature_types': ['ATAC'],
        'status': 'current',
    }
    result = upgrader.upgrade(
        'droplet_based_library', value, current_version='2', target_version='3'
    )
    assert result['schema_version'] == '3'
    assert result['feature_types'] == ['ATAC']


def test_droplet_based_library_upgrade_2_3_replaces_empty_feature_types(upgrader):
    value = {
        'schema_version': '2',
        'feature_types': [],
        'status': 'current',
    }
    result = upgrader.upgrade(
        'droplet_based_library', value, current_version='2', target_version='3'
    )
    assert result['schema_version'] == '3'
    assert result['feature_types'] == ['Gene Expression']


def test_plate_based_library_upgrade_3_4_defaults_feature_types(upgrader):
    value = {
        'schema_version': '3',
        'status': 'current',
    }
    result = upgrader.upgrade(
        'plate_based_library', value, current_version='3', target_version='4'
    )
    assert result['schema_version'] == '4'
    assert result['feature_types'] == ['Gene Expression']


def test_plate_based_library_upgrade_3_4_preserves_feature_types(upgrader):
    value = {
        'schema_version': '3',
        'feature_types': ['Multiplexing Capture'],
        'status': 'current',
    }
    result = upgrader.upgrade(
        'plate_based_library', value, current_version='3', target_version='4'
    )
    assert result['schema_version'] == '4'
    assert result['feature_types'] == ['Multiplexing Capture']


def test_droplet_based_library_upgrade_3_4_preserves_multiplexing_method(upgrader):
    value = {
        'schema_version': '3',
        'samples': SINGLE_SAMPLE,
        'multiplexing_method': ['antibody hashing'],
        'status': 'current',
    }
    result = upgrader.upgrade(
        'droplet_based_library', value, current_version='3', target_version='4'
    )
    assert result['schema_version'] == '4'
    assert result['multiplexing_method'] == ['antibody hashing']
    assert result['samples'] == SINGLE_SAMPLE


def test_plate_based_library_upgrade_4_5_preserves_multiplexing_method(upgrader):
    value = {
        'schema_version': '4',
        'samples': SINGLE_SAMPLE,
        'multiplexing_method': ['combinatorial indexing'],
        'status': 'current',
    }
    result = upgrader.upgrade(
        'plate_based_library', value, current_version='4', target_version='5'
    )
    assert result['schema_version'] == '5'
    assert result['multiplexing_method'] == ['combinatorial indexing']
    assert result['samples'] == SINGLE_SAMPLE


@pytest.mark.parametrize(
    ('item_type', 'current_version', 'target_version'),
    [
        ('droplet_based_library', '4', '5'),
        ('plate_based_library', '5', '6'),
    ],
)
def test_library_upgrade_preserves_invalid_dbxrefs_in_notes(
    upgrader, item_type, current_version, target_version
):
    value = {
        'schema_version': current_version,
        'dbxrefs': ['SRA:SRX67890', 'GEO:GSM12345', 'GEO-obsolete:GSM12345'],
        'notes': 'Existing internal context.',
    }
    result = upgrader.upgrade(
        item_type,
        value,
        current_version=current_version,
        target_version=target_version,
    )
    assert result['schema_version'] == target_version
    assert result['dbxrefs'] == ['SRA:SRX67890', 'GEO:GSM12345']
    assert result['notes'] == (
        'Existing internal context. '
        'Legacy dbxrefs removed during schema upgrade: GEO-obsolete:GSM12345.'
    )


def test_library_upgrade_removes_all_invalid_dbxrefs(upgrader):
    value = {
        'schema_version': '4',
        'dbxrefs': ['GEO-obsolete:GSM12345', 'GEO-obsolete:GSM67890'],
    }
    result = upgrader.upgrade(
        'droplet_based_library',
        value,
        current_version='4',
        target_version='5',
    )
    assert 'dbxrefs' not in result
    assert result['notes'] == (
        'Legacy dbxrefs removed during schema upgrade: '
        'GEO-obsolete:GSM12345, GEO-obsolete:GSM67890.'
    )


@pytest.mark.parametrize('dbxrefs', [ABSENT, None, []])
def test_library_upgrade_without_dbxrefs_does_not_add_notes(upgrader, dbxrefs):
    value = {'schema_version': '5'}
    if dbxrefs is not ABSENT:
        value['dbxrefs'] = dbxrefs
    result = upgrader.upgrade(
        'plate_based_library',
        value,
        current_version='5',
        target_version='6',
    )
    assert 'dbxrefs' not in result
    assert 'notes' not in result


# The Library dbxrefs pattern as released with droplet_based_library 5 / plate_based_library 6.
LIBRARY_DBXREF_PATTERN_AS_RELEASED = (
    r'^(Biomaterial:SAM(E|N|D)(A|G)?\d+|Biomaterial:EGAN\d+|SRA:SRS\d+|ENA:ERS\d+|'
    r'GEO:GSM\d+|SRA:SRX\d+|ENA:ERX\d+|EGA:EGAX\d+)$'
)


def test_library_upgrade_dbxref_pattern_is_frozen():
    # The 4->5 and 5->6 steps are historical. Editing their pattern would retroactively
    # change which values they strip into admin-only notes, so it is pinned to a literal
    # rather than to whatever library.json currently says.
    from igvfd.upgrade.library import LIBRARY_DBXREF_PATTERN

    assert LIBRARY_DBXREF_PATTERN.pattern == LIBRARY_DBXREF_PATTERN_AS_RELEASED, (
        'The released upgrade steps must keep stripping exactly what they stripped on '
        'release. Do not edit LIBRARY_DBXREF_PATTERN to match a new schema pattern; add '
        'a new constant and a new upgrade step instead.'
    )


def test_library_upgrade_dbxref_pattern_matches_schema():
    # Guards the other direction: at authoring time the constant must equal the schema it
    # filters for, so a widened schema cannot leave the upgrade stripping valid values.
    from snovault.schema_utils import load_schema

    from igvfd.upgrade.library import LIBRARY_DBXREF_PATTERN

    schema = load_schema('igvfd:schemas/library.json')
    assert LIBRARY_DBXREF_PATTERN.pattern == schema['properties']['dbxrefs']['items']['pattern'], (
        'library.json dbxrefs pattern changed. Freeze the current constant under a '
        'versioned name for the released steps, add a new constant plus upgrade step for '
        'the new pattern, and point this test at the new constant. '
        'test_library_upgrade_dbxref_pattern_is_frozen imports the constant by name, so '
        'update its import and LIBRARY_DBXREF_PATTERN_AS_RELEASED in the same change.'
    )


def test_library_upgrade_keeps_valid_dbxrefs_and_leaves_notes_untouched(upgrader):
    # Nothing to migrate: dbxrefs and any pre-existing notes must both survive verbatim.
    value = {
        'schema_version': '4',
        'dbxrefs': ['Biomaterial:SAMN53299868', 'EGA:EGAX12345', 'GEO:GSM12345'],
        'notes': 'Existing internal context.',
    }
    result = upgrader.upgrade(
        'droplet_based_library',
        value,
        current_version='4',
        target_version='5',
    )
    assert result['dbxrefs'] == ['Biomaterial:SAMN53299868', 'EGA:EGAX12345', 'GEO:GSM12345']
    assert result['notes'] == 'Existing internal context.'


def test_library_upgrade_handles_null_notes(upgrader):
    # A legacy object can carry notes: null; the helper must not choke on it.
    value = {
        'schema_version': '4',
        'dbxrefs': ['GEO-obsolete:GSM12345'],
        'notes': None,
    }
    result = upgrader.upgrade(
        'droplet_based_library',
        value,
        current_version='4',
        target_version='5',
    )
    assert 'dbxrefs' not in result
    assert result['notes'] == (
        'Legacy dbxrefs removed during schema upgrade: GEO-obsolete:GSM12345.'
    )


def test_library_upgrade_does_not_strip_what_the_validator_accepts(upgrader):
    # Compatibility shim, not an endorsement: a trailing newline in a dbxref is dirty
    # data, but JSON Schema `pattern` is an unanchored search in which `$` matches before
    # one, so the validator accepts it. The upgrade must agree with the validator rather
    # than quietly moving a value the schema permits into admin-only notes. If the
    # patterns are ever changed to `\Z`, this test should flip to asserting removal.
    value = {
        'schema_version': '4',
        'dbxrefs': ['GEO:GSM12345\n'],
    }
    result = upgrader.upgrade(
        'droplet_based_library',
        value,
        current_version='4',
        target_version='5',
    )
    assert result['dbxrefs'] == ['GEO:GSM12345\n']
    assert 'notes' not in result


@pytest.mark.parametrize(
    'existing_notes',
    [None, '', '   ', 'Existing context', 'Existing context.'],
)
def test_library_upgrade_note_satisfies_notes_schema(upgrader, existing_notes):
    # The note is written as free text into `notes`, which is itself constrained by the
    # schema (no leading/trailing whitespace). Nothing else validates the string the
    # upgrade produces, so assert it against the real pattern for every starting state.
    from snovault.schema_utils import load_schema

    notes_pattern = re.compile(
        load_schema('igvfd:schemas/library.json')['properties']['notes']['pattern']
    )
    value = {'schema_version': '4', 'dbxrefs': ['GEO-obsolete:GSM12345']}
    if existing_notes is not None:
        value['notes'] = existing_notes
    result = upgrader.upgrade(
        'droplet_based_library',
        value,
        current_version='4',
        target_version='5',
    )
    assert notes_pattern.search(result['notes']), repr(result['notes'])


def test_biosample_upgrade_note_satisfies_notes_schema(upgrader):
    # Same guarantee for the Biosample path, where every value is preserved.
    from snovault.schema_utils import load_schema

    notes_pattern = re.compile(
        load_schema('igvfd:schemas/tissue.json')['properties']['notes']['pattern']
    )
    result = upgrader.upgrade(
        'tissue',
        {'schema_version': '3', 'dbxrefs': ['BioSample:SAMN53299868', 'SRA:SRS12345']},
        current_version='3',
        target_version='4',
    )
    assert notes_pattern.search(result['notes']), repr(result['notes'])
