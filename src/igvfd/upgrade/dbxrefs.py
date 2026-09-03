def preserve_invalid_dbxrefs(value, valid_pattern=None):
    """Drop dbxrefs the current schema rejects, preserving them verbatim in notes.

    A valid_pattern of None means the schema no longer defines dbxrefs at all, so
    every value is rejected. notes is admin_only, so preserved values are visible
    to admins for manual reconciliation.
    """
    dbxrefs = value.get('dbxrefs')
    if dbxrefs is None:
        return
    if not dbxrefs:
        value.pop('dbxrefs')
        return

    valid_dbxrefs = []
    invalid_dbxrefs = []
    for dbxref in dbxrefs:
        is_valid = valid_pattern is not None and valid_pattern.fullmatch(dbxref)
        target = valid_dbxrefs if is_valid else invalid_dbxrefs
        target.append(dbxref)

    if valid_dbxrefs:
        value['dbxrefs'] = valid_dbxrefs
    else:
        value.pop('dbxrefs')

    if not invalid_dbxrefs:
        return

    upgrade_note = (
        'Legacy dbxrefs removed during schema upgrade: '
        f'{", ".join(invalid_dbxrefs)}.'
    )
    existing_notes = value.get('notes', '').strip()
    value['notes'] = f'{existing_notes} {upgrade_note}'.strip()


def remove_all_dbxrefs(value):
    """Drop the dbxrefs property entirely, preserving every value in notes."""
    preserve_invalid_dbxrefs(value, valid_pattern=None)
