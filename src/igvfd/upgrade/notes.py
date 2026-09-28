def append_upgrade_note(value, upgrade_note):
    """Append upgrade_note to notes, which is admin_only, for manual reconciliation."""
    # Separate with a newline rather than a space so the appended sentence never runs
    # into a pre-existing note, and without rewriting text the upgrade does not own.
    existing_notes = (value.get('notes') or '').strip()
    value['notes'] = f'{existing_notes}\n{upgrade_note}'.strip() if existing_notes else upgrade_note
