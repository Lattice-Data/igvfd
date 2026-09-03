def preserve_invalid_dbxrefs(value, valid_pattern=None):
    """Drop dbxrefs the current schema rejects, preserving them verbatim in notes.

    A valid_pattern of None means the schema no longer defines dbxrefs at all, so
    every value is rejected. notes is admin_only, so preserved values are visible
    to admins for manual reconciliation.
    """
    if 'dbxrefs' not in value:
        return
    dbxrefs = value['dbxrefs']
    if not dbxrefs or valid_pattern is None:
        # No pattern means the schema no longer defines dbxrefs, so nothing is valid.
        value.pop('dbxrefs')
        if dbxrefs:
            _append_upgrade_note(value, dbxrefs)
        return

    valid_dbxrefs = []
    invalid_dbxrefs = []
    for dbxref in dbxrefs:
        # search, not fullmatch: JSON Schema `pattern` is an unanchored search, and `$`
        # also matches before a trailing newline. fullmatch would strip values the
        # schema itself accepts, e.g. 'GEO:GSM123\n', into admin-only notes.
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
    existing_notes = (value.get('notes') or '').strip()
    if existing_notes and existing_notes[-1] not in '.!?':
        existing_notes = f'{existing_notes}.'
    value['notes'] = f'{existing_notes} {upgrade_note}'.strip()


def remove_all_dbxrefs(value):
    """Drop the dbxrefs property entirely, preserving every value in notes."""
    preserve_invalid_dbxrefs(value, valid_pattern=None)
