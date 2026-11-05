import re

from snovault.upgrader import upgrade_step

from .aliases import preserve_invalid_aliases
from .dbxrefs import preserve_invalid_dbxrefs


# The dbxrefs pattern as of controlled_term 3. The step below is historical once
# released, so this value must not be edited to track a later schema change: doing so
# would retroactively alter which values it strips. When controlled_term.json's pattern
# next changes, freeze this constant under a versioned name for the existing step and add
# a new constant for the new step. See
# test_controlled_term_upgrade_dbxref_pattern_matches_schema.
CONTROLLED_TERM_DBXREF_PATTERN = re.compile(
    r'^(PMID:[0-9]+|DOI:10\.[0-9]+/.+|CAS:\d{2,7}-\d{2}-\d)(?![\s\S])'
)


# The ControlledTerm aliases pattern as of controlled_term 5: lattice:<ontology>_<term>,
# lowercase letters, digits and single underscores only. Historical once released, like
# the constant above; see test_controlled_term_upgrade_alias_pattern_matches_schema.
CONTROLLED_TERM_ALIAS_PATTERN = re.compile(
    r'^lattice:[a-z0-9]+(?:_[a-z0-9]+)+(?![\s\S])'
)


@upgrade_step('controlled_term', '1', '2')
def controlled_term_1_2(value, system):
    value.pop('term_name', None)


@upgrade_step('controlled_term', '2', '3')
def controlled_term_2_3(value, system):
    preserve_invalid_dbxrefs(value, CONTROLLED_TERM_DBXREF_PATTERN)


@upgrade_step('controlled_term', '3', '4')
def controlled_term_3_4(value, system):
    preserve_invalid_aliases(value)


@upgrade_step('controlled_term', '4', '5')
def controlled_term_4_5(value, system):
    # Stage 1 of DB2-84 added a compliant alias to every stored term before this step was
    # released, so it removes only the legacy aliases; they stay readable in notes.
    preserve_invalid_aliases(value, CONTROLLED_TERM_ALIAS_PATTERN)
