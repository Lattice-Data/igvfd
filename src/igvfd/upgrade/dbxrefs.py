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
        # search, not fullmatch, to agree with the validator this filters for. Note the
        # reason is a Python implementation detail, not JSON Schema semantics: jsonschema
        # compiles with Python `re`, where `$` also matches before a trailing newline, so
        # 'GEO:GSM123\n' validates here. ECMA-262 -- the dialect JSON Schema specifies --
        # rejects it. fullmatch would strip values this server accepts into admin-only
        # notes; see docs/dbxrefs_patterns.md for the divergence and the portable fix.
        target = valid_dbxrefs if valid_pattern.search(dbxref) else invalid_dbxrefs
        target.append(dbxref)

    if valid_dbxrefs:
        value['dbxrefs'] = valid_dbxrefs
    else:
        value.pop('dbxrefs')

    if invalid_dbxrefs:
        _append_upgrade_note(value, invalid_dbxrefs)


def _append_upgrade_note(value, removed_dbxrefs):
    upgrade_note = (
        'Legacy dbxrefs removed during schema upgrade: '
        f'{", ".join(removed_dbxrefs)}.'
    )
    # Separate with a newline rather than a space so the appended sentence never runs
    # into a pre-existing note, and without rewriting text the upgrade does not own.
    existing_notes = (value.get('notes') or '').strip()
    value['notes'] = f'{existing_notes}\n{upgrade_note}'.strip() if existing_notes else upgrade_note


def remove_all_dbxrefs(value):
    """Drop the dbxrefs property entirely, preserving every value in notes."""
    preserve_invalid_dbxrefs(value, valid_pattern=None)
