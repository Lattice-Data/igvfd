from .notes import append_upgrade_note


def preserve_invalid_dbxrefs(value, valid_pattern):
    """Drop dbxrefs the current schema rejects, preserving them verbatim in notes.

    valid_pattern is the compiled pattern the schema now enforces, or None when the
    schema no longer defines dbxrefs at all and every value is therefore rejected.
    notes is admin_only, so preserved values are visible to admins for manual
    reconciliation.
    """
    if 'dbxrefs' not in value:
        return
    dbxrefs = value['dbxrefs']

    if not dbxrefs:
        # Empty or null: nothing to preserve, and the property no longer validates.
        value.pop('dbxrefs')
        return

    if valid_pattern is None:
        # The property is gone from the schema, so every value is preserved.
        value.pop('dbxrefs')
        _append_upgrade_note(value, dbxrefs)
        return

    valid_dbxrefs = []
    invalid_dbxrefs = []
    for dbxref in dbxrefs:
        # search, matching how jsonschema applies `pattern`, so this filters exactly as
        # the validator does. The patterns end with `(?![\s\S])` rather than `$`, so both
        # anchor at true end of input and search and fullmatch coincide.
        target = valid_dbxrefs if valid_pattern.search(dbxref) else invalid_dbxrefs
        target.append(dbxref)

    if valid_dbxrefs:
        value['dbxrefs'] = valid_dbxrefs
    else:
        value.pop('dbxrefs')

    if invalid_dbxrefs:
        _append_upgrade_note(value, invalid_dbxrefs)


def _append_upgrade_note(value, removed_dbxrefs):
    append_upgrade_note(
        value,
        'Legacy dbxrefs removed during schema upgrade: '
        f'{", ".join(removed_dbxrefs)}.'
    )


def remove_all_dbxrefs(value):
    """Drop the dbxrefs property entirely, preserving every value in notes."""
    preserve_invalid_dbxrefs(value, valid_pattern=None)
