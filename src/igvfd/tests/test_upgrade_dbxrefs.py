import re

from igvfd.upgrade.dbxrefs import preserve_invalid_dbxrefs

VALID_PATTERN = re.compile(r'^SRA:SRS\d+$')

UPGRADE_NOTE = 'Legacy dbxrefs removed during schema upgrade: BioSample:SAMN53299868.'


def test_preserve_invalid_dbxrefs_records_note_once_when_reapplied():
    value = {'dbxrefs': ['SRA:SRS12345', 'BioSample:SAMN53299868']}

    preserve_invalid_dbxrefs(value, VALID_PATTERN)
    assert value['dbxrefs'] == ['SRA:SRS12345']
    assert value['notes'] == UPGRADE_NOTE

    # An object re-migrated with the same rejected identifier must not accumulate the note.
    value['dbxrefs'] = ['SRA:SRS12345', 'BioSample:SAMN53299868']
    preserve_invalid_dbxrefs(value, VALID_PATTERN)
    assert value['dbxrefs'] == ['SRA:SRS12345']
    assert value['notes'] == UPGRADE_NOTE
    assert value['notes'].count('Legacy dbxrefs removed') == 1
