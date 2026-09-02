from re import Pattern


def preserve_invalid_dbxrefs(value, valid_pattern: Pattern[str]):
    dbxrefs = value.get('dbxrefs')
    if dbxrefs is None:
        return
    if not dbxrefs:
        value.pop('dbxrefs')
        return

    valid_dbxrefs = []
    invalid_dbxrefs = []
    for dbxref in dbxrefs:
        target = valid_dbxrefs if valid_pattern.fullmatch(dbxref) else invalid_dbxrefs
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
