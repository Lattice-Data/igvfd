import pytest


pytestmark = [pytest.mark.indexing]


EXPECTED_HEADER_PREFIX = [
    'File ID',
    'File aliases',
    'File format',
    'File set ID',
    'File set type',
    'File set aliases',
    'File set summary',
    'File set status',
    'File set description',
    'File set lab',
    'Submitted by',
    'Creation timestamp',
]

EXPECTED_AUDIT_COLUMNS = [
    'Audit WARNING',
    'Audit NOT_COMPLIANT',
    'Audit ERROR',
]


def _parse_tsv(response):
    lines = [line for line in response.text.strip().splitlines() if line]
    return [line.split('\t') for line in lines]


def test_matrix_file_set_metadata_get(workbook, testapp):
    r = testapp.get('/matrix-file-set-metadata/?type=MatrixFileSet')
    assert r.content_type == 'text/tsv'
    assert r.content_disposition == 'attachment; filename="matrix_file_set_metadata.tsv"'
    rows = _parse_tsv(r)
    assert rows, 'expected header and data rows'
    header = rows[0]
    assert header[:len(EXPECTED_HEADER_PREFIX)] == EXPECTED_HEADER_PREFIX
    assert header[-3:] == EXPECTED_AUDIT_COLUMNS
    # Workbook includes a MatrixFileSet with both raw and processed files.
    assert len(rows) >= 3  # header + at least two file rows overall
    file_ids = [row[0] for row in rows[1:]]
    assert any('/raw_matrix_files/' in file_id for file_id in file_ids)
    assert any('/processed_matrix_files/' in file_id for file_id in file_ids)
    type_cells = [row[4] for row in rows[1:]]
    assert all('MatrixFileSet' in cell for cell in type_cells)


def test_matrix_file_set_metadata_post_with_elements(workbook, testapp):
    search = testapp.get(
        '/search/?type=MatrixFileSet&aliases=lattice:mfs-raw-and-processed'
    )
    assert search.json['@graph'], 'expected workbook MatrixFileSet insert'
    file_set_id = search.json['@graph'][0]['@id']
    r = testapp.post_json(
        '/matrix-file-set-metadata/?type=MatrixFileSet',
        {'elements': [file_set_id]},
    )
    assert r.content_type == 'text/tsv'
    assert r.content_disposition == 'attachment; filename="matrix_file_set_metadata.tsv"'
    rows = _parse_tsv(r)
    assert rows[0][-3:] == EXPECTED_AUDIT_COLUMNS
    # One MatrixFileSet with one raw + one processed file -> two data rows.
    assert len(rows) == 3
    file_ids = {row[0] for row in rows[1:]}
    assert any('/raw_matrix_files/' in file_id for file_id in file_ids)
    assert any('/processed_matrix_files/' in file_id for file_id in file_ids)
    assert all(row[3] == file_set_id for row in rows[1:])


def test_matrix_file_set_metadata_rejects_wrong_type(workbook, testapp):
    testapp.get('/matrix-file-set-metadata/?type=SequenceFileSet', status=400)
    testapp.get('/matrix-file-set-metadata/', status=400)


def test_matrix_file_set_metadata_rejects_legacy_files_filter(workbook, testapp):
    testapp.get(
        '/matrix-file-set-metadata/?type=MatrixFileSet&files.file_format=h5ad',
        status=400,
    )


def test_matrix_file_set_metadata_rejects_negated_file_filter(workbook, testapp):
    testapp.get(
        '/matrix-file-set-metadata/?type=MatrixFileSet&processed_matrix_files.file_format!=h5ad',
        status=400,
    )


def test_matrix_file_set_metadata_file_format_filter(workbook, testapp):
    r = testapp.get(
        '/matrix-file-set-metadata/?type=MatrixFileSet&processed_matrix_files.file_format=h5ad'
    )
    rows = _parse_tsv(r)
    assert rows[0][2] == 'File format'
    assert len(rows) > 1, 'expected at least one h5ad file row'
    formats = {row[2] for row in rows[1:]}
    assert formats == {'h5ad'}
    file_ids = [row[0] for row in rows[1:]]
    assert all('/processed_matrix_files/' in file_id for file_id in file_ids)


def test_matrix_file_set_metadata_observation_count_inequality_filter(workbook, testapp):
    r = testapp.get(
        '/matrix-file-set-metadata/?type=MatrixFileSet'
        '&raw_matrix_files.observation_count=gte:12000'
    )
    rows = _parse_tsv(r)
    assert len(rows) > 1, 'expected at least one matching file row'
    file_ids = [row[0] for row in rows[1:]]
    assert all('/raw_matrix_files/' in file_id for file_id in file_ids)
    assert not any('/processed_matrix_files/' in file_id for file_id in file_ids)


def test_matrix_file_set_metadata_both_link_fields_filtered(workbook, testapp):
    r = testapp.get(
        '/matrix-file-set-metadata/?type=MatrixFileSet'
        '&raw_matrix_files.file_format=h5'
        '&processed_matrix_files.file_format=h5ad'
    )
    rows = _parse_tsv(r)
    assert len(rows) > 1, 'expected matching rows from both link fields'
    file_ids = [row[0] for row in rows[1:]]
    # Both arrays are filtered, so both are reported (each scoped to its filter).
    assert any('/raw_matrix_files/' in file_id for file_id in file_ids)
    assert any('/processed_matrix_files/' in file_id for file_id in file_ids)
