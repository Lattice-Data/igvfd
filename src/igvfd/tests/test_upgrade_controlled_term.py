import re

import pytest
from snovault.schema_utils import load_schema

# Distinguishes an absent dbxrefs key from an explicit null.
ABSENT_DBXREFS = object()


def test_controlled_term_upgrade_1_2_removes_term_name(upgrader):
    value = {
        'schema_version': '1',
        'term_id': 'CL:0000001',
        'ontology_source': 'CL',
        'term_name': 'legacy stored label',
        'status': 'current',
    }
    result = upgrader.upgrade(
        'controlled_term', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'term_name' not in result


def test_controlled_term_upgrade_1_2_without_term_name(upgrader):
    value = {
        'schema_version': '1',
        'term_id': 'CL:0000002',
        'ontology_source': 'CL',
        'status': 'current',
    }
    result = upgrader.upgrade(
        'controlled_term', value, current_version='1', target_version='2'
    )
    assert result['schema_version'] == '2'
    assert 'term_name' not in result


# The ControlledTerm dbxrefs pattern as released with controlled_term 3.
CONTROLLED_TERM_DBXREF_PATTERN_AS_RELEASED = (
    r'^(PMID:[0-9]+|DOI:10\.[0-9]+/.+|CAS:\d{2,7}-\d{2}-\d)(?![\s\S])'
)


def test_controlled_term_upgrade_dbxref_pattern_is_frozen():
    from igvfd.upgrade.controlled_term import CONTROLLED_TERM_DBXREF_PATTERN

    assert CONTROLLED_TERM_DBXREF_PATTERN.pattern == CONTROLLED_TERM_DBXREF_PATTERN_AS_RELEASED, (
        'The released 2->3 step must keep stripping exactly what it stripped on release. '
        'Add a new constant and step rather than editing this one.'
    )


def test_controlled_term_upgrade_dbxref_pattern_matches_schema():
    from igvfd.upgrade.controlled_term import CONTROLLED_TERM_DBXREF_PATTERN

    schema = load_schema('igvfd:schemas/controlled_term.json')
    assert CONTROLLED_TERM_DBXREF_PATTERN.pattern == schema['properties']['dbxrefs']['items']['pattern'], (
        'controlled_term.json dbxrefs pattern changed. Freeze the current constant under '
        'a versioned name for the released step, add a new constant plus step, and point '
        'this test and CONTROLLED_TERM_DBXREF_PATTERN_AS_RELEASED at the new constant.'
    )


def test_controlled_term_upgrade_2_3_keeps_valid_dbxrefs(upgrader):
    value = {
        'schema_version': '2',
        'dbxrefs': ['PMID:12345678', 'CAS:50-00-0', 'DOI:10.1234/test'],
        'notes': 'Existing context.',
    }
    result = upgrader.upgrade('controlled_term', value, current_version='2', target_version='3')
    assert result['schema_version'] == '3'
    assert result['dbxrefs'] == ['PMID:12345678', 'CAS:50-00-0', 'DOI:10.1234/test']
    assert result['notes'] == 'Existing context.'


def test_controlled_term_upgrade_2_3_preserves_invalid_dbxrefs_in_notes(upgrader):
    value = {
        'schema_version': '2',
        'dbxrefs': ['PMID:12345678', 'PMID:12345678\n', '50-00-0'],
    }
    result = upgrader.upgrade('controlled_term', value, current_version='2', target_version='3')
    assert result['dbxrefs'] == ['PMID:12345678']
    assert result['notes'] == (
        'Legacy dbxrefs removed during schema upgrade: PMID:12345678\n, 50-00-0.'
    )


def test_controlled_term_upgrade_2_3_note_satisfies_notes_schema(upgrader):
    notes_pattern = re.compile(
        load_schema('igvfd:schemas/controlled_term.json')['properties']['notes']['pattern']
    )
    result = upgrader.upgrade(
        'controlled_term',
        {'schema_version': '2', 'dbxrefs': ['not-an-identifier']},
        current_version='2',
        target_version='3',
    )
    assert 'dbxrefs' not in result
    assert notes_pattern.search(result['notes']), repr(result['notes'])


@pytest.mark.parametrize('dbxrefs', [ABSENT_DBXREFS, None, []])
def test_controlled_term_upgrade_2_3_without_dbxrefs_does_not_add_notes(upgrader, dbxrefs):
    value = {'schema_version': '2'}
    if dbxrefs is not ABSENT_DBXREFS:
        value['dbxrefs'] = dbxrefs
    result = upgrader.upgrade('controlled_term', value, current_version='2', target_version='3')
    assert 'dbxrefs' not in result
    assert 'notes' not in result
