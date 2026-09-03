import re

from snovault.upgrader import upgrade_step

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


@upgrade_step('controlled_term', '1', '2')
def controlled_term_1_2(value, system):
    value.pop('term_name', None)


@upgrade_step('controlled_term', '2', '3')
def controlled_term_2_3(value, system):
    preserve_invalid_dbxrefs(value, CONTROLLED_TERM_DBXREF_PATTERN)
