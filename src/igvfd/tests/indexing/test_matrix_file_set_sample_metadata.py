import pytest
import re


pytestmark = [pytest.mark.indexing]


# Target column order is an NCBI BioSample submission template. '*' marks the
# NCBI-required columns and is part of the literal header text.
EXPECTED_HEADER = [
    '*sample_name',
    'sample_title',
    'bioproject_accession',
    'library_id',
    '*organism',
    '*isolate',
    '*age',
    '*biomaterial_provider',
    '*collection_date',
    '*geo_loc_name',
    '*sex',
    '*tissue',
    'cell_line',
    'cell_subtype',
    'samples',
    'sample: sample_probe_barcode',
    'perturbation_strategy',
    'perturbation_system_type',
    'experimental_perturbation_factors',
    'experimental_perturbation_timepoint',
    'ethnicity',
    'health_state',
    'karyotype',
    'phenotype',
    'population',
    'race',
    'sample_type',
    'treatment',
    'description',
]

EXPECTED_AUDIT_COLUMNS = [
    'Audit WARNING',
    'Audit NOT_COMPLIANT',
    'Audit ERROR',
]

PLACEHOLDER_COLUMNS = [
    'sample_title',
    'bioproject_accession',
    '*isolate',
    'samples',
    'perturbation_system_type',
    'karyotype',
    'phenotype',
    'population',
    'race',
]

# The workbook tissue reachable from every MatrixFileSet: lattice:tissue-frozen-basic.
WORKBOOK_SAMPLE_ALIAS = 'tissue-frozen-basic'


def _parse_tsv(response):
    lines = [line for line in response.text.strip().splitlines() if line]
    return [line.split('\t') for line in lines]


def _rows_as_dicts(rows):
    header = rows[0]
    return [dict(zip(header, row)) for row in rows[1:]]


def _normalize_numbers(cell):
    # Schema 'number' properties may round-trip as 37 or 37.0; the column content is
    # what matters here, not which of the two JSON renders it through.
    return re.sub(r'(\d)\.0\b', r'\1', cell)


def _get_file_set_id(testapp, alias):
    search = testapp.get(f'/search/?type=MatrixFileSet&aliases=lattice:{alias}')
    assert search.json['@graph'], f'expected workbook MatrixFileSet {alias}'
    return search.json['@graph'][0]['@id']


def test_sample_metadata_header_and_content_type(workbook, testapp):
    r = testapp.get('/matrix-file-set-sample-metadata/?type=MatrixFileSet')
    assert r.content_type == 'text/tsv'
    assert r.content_disposition == (
        'attachment; filename="matrix_file_set_sample_metadata.tsv"'
    )
    rows = _parse_tsv(r)
    assert rows, 'expected at least a header row'
    assert rows[0] == EXPECTED_HEADER + EXPECTED_AUDIT_COLUMNS


def test_sample_metadata_dedupes_to_one_row_per_sample(workbook, testapp):
    # The file set holds one raw + one processed matrix file and both point at the
    # same biosample, so the sample-centric table must collapse to a single row.
    file_set_id = _get_file_set_id(testapp, 'mfs-raw-and-processed')
    r = testapp.post_json(
        '/matrix-file-set-sample-metadata/?type=MatrixFileSet',
        {'elements': [file_set_id]},
    )
    rows = _parse_tsv(r)
    assert len(rows) == 2, 'expected header + exactly one deduped sample row'
    row = _rows_as_dicts(rows)[0]
    assert row['*sample_name'] == WORKBOOK_SAMPLE_ALIAS


def test_sample_metadata_cells_from_workbook_sample(workbook, testapp):
    file_set_id = _get_file_set_id(testapp, 'mfs-raw-and-processed')
    r = testapp.post_json(
        '/matrix-file-set-sample-metadata/?type=MatrixFileSet',
        {'elements': [file_set_id]},
    )
    row = _rows_as_dicts(_parse_tsv(r))[0]
    # sample_name strips the 'lattice:' alias prefix.
    assert row['*sample_name'] == WORKBOOK_SAMPLE_ALIAS
    # Donor fields resolve through the extended donors include.
    assert row['*organism'] == 'Homo sapiens'
    assert row['*sex'] == 'unspecified'
    # Ontology term names resolve from the reference database built into the image.
    assert row['*tissue'] == 'uterine cervix'
    assert row['*age'] == 'embryonic stage'
    assert row['sample: sample_probe_barcode'] == 'P01-A1'
    assert row['sample_type'] == 'tissue'
    assert row['description'] == 'Test tissue sample 1'
    # library_id comes from the embedded libraries reverse link.
    assert row['library_id'] == 'INSERT-DROPLET-CRO-GROUP-1'
    # Collection columns. Asserted with real values because a blank cell cannot
    # distinguish a correct mapping with no data from a broken path.
    assert row['*biomaterial_provider'] == 'Sigma-Aldrich'
    assert row['*collection_date'] == '2024-01-15'
    assert row['*geo_loc_name'] == 'USA'


def test_sample_metadata_placeholder_columns(workbook, testapp):
    file_set_id = _get_file_set_id(testapp, 'mfs-raw-and-processed')
    r = testapp.post_json(
        '/matrix-file-set-sample-metadata/?type=MatrixFileSet',
        {'elements': [file_set_id]},
    )
    row = _rows_as_dicts(_parse_tsv(r))[0]
    for column in PLACEHOLDER_COLUMNS:
        assert row[column] == 'placeholder', f'{column} should be a placeholder'


def test_sample_metadata_subtype_keyed_columns_are_blank_off_type(workbook, testapp):
    # The workbook sample is a Tissue, so the CellLine-only column stays empty and
    # cell_subtype reads enriched_cell_types (unset here) rather than intended_cell_types.
    file_set_id = _get_file_set_id(testapp, 'mfs-raw-and-processed')
    r = testapp.post_json(
        '/matrix-file-set-sample-metadata/?type=MatrixFileSet',
        {'elements': [file_set_id]},
    )
    row = _rows_as_dicts(_parse_tsv(r))[0]
    assert row['cell_line'] == ''
    assert row['cell_subtype'] == ''


def test_sample_metadata_empty_case_returns_header_only(workbook, testapp):
    # This file set's only matrix file has no samples, so no sample rows exist.
    file_set_id = _get_file_set_id(testapp, 'mfs-no-samples')
    r = testapp.post_json(
        '/matrix-file-set-sample-metadata/?type=MatrixFileSet',
        {'elements': [file_set_id]},
    )
    assert r.content_type == 'text/tsv'
    rows = _parse_tsv(r)
    assert len(rows) == 1, 'expected header only'
    assert rows[0] == EXPECTED_HEADER + EXPECTED_AUDIT_COLUMNS


def _get_multi_sample_rows(testapp):
    file_set_id = _get_file_set_id(testapp, 'mfs-multi-sample')
    r = testapp.post_json(
        '/matrix-file-set-sample-metadata/?type=MatrixFileSet',
        {'elements': [file_set_id]},
    )
    return {row['*sample_name']: row for row in _rows_as_dicts(_parse_tsv(r))}


def test_sample_metadata_one_row_per_distinct_sample(workbook, testapp):
    # A single matrix file carrying three distinct biosamples yields three rows.
    rows = _get_multi_sample_rows(testapp)
    assert set(rows) == {
        'tissue-cultured-treated',
        'cell-line-reference',
        'organoid-brain',
    }


def test_sample_metadata_composed_perturbation_cells(workbook, testapp):
    # Composed cells are built per source object, so bounds and units cannot be
    # paired across different treatments or conditions.
    row = _get_multi_sample_rows(testapp)['tissue-cultured-treated']
    assert _normalize_numbers(row['treatment']) == 'vitamin D 10 mg/kg'
    assert _normalize_numbers(row['experimental_perturbation_timepoint']) == '24-48 hour'
    factors = _normalize_numbers(row['experimental_perturbation_factors'])
    # Two conditions, separator-joined and sorted.
    assert factors == 'pH 7.4 pH units; temperature 37 celsius'


def test_sample_metadata_new_embed_edges_resolve(workbook, testapp):
    # Each of these columns depends on a Path added for this endpoint, so a blank
    # here means the embed stopped resolving rather than the data being absent.
    row = _get_multi_sample_rows(testapp)['tissue-cultured-treated']
    assert row['perturbation_strategy'] == 'knockout screen'
    assert row['health_state'] == 'type 2 diabetes mellitus'
    assert row['ethnicity'] == '10x gene expression flex'


def test_sample_metadata_multivalued_cells_use_separator(workbook, testapp):
    # This tissue has two human donors, one female and one unspecified.
    row = _get_multi_sample_rows(testapp)['tissue-cultured-treated']
    assert row['*sex'] == 'female; unspecified'
    # Both donors are Homo sapiens, so the repeated value collapses to one.
    assert row['*organism'] == 'Homo sapiens'


def test_sample_metadata_cell_line_row_column_rules(workbook, testapp):
    row = _get_multi_sample_rows(testapp)['cell-line-reference']
    assert row['sample_type'] == 'cell line'
    # sample_terms feeds cell_line on a CellLine row and tissue stays empty.
    assert row['cell_line'] == 'primary cultured cell'
    assert row['*tissue'] == ''
    # CellLine and Organoid take cell_subtype from intended_cell_types.
    assert row['cell_subtype'] == 'primary cultured cell'


def test_sample_metadata_organoid_row_column_rules(workbook, testapp):
    row = _get_multi_sample_rows(testapp)['organoid-brain']
    assert row['sample_type'] == 'organoid'
    # An Organoid takes tissue from sample_terms, unlike a CellLine.
    assert row['*tissue'] == 'uterine cervix'
    assert row['cell_line'] == ''
    assert row['cell_subtype'] == 'primary cultured cell'


def test_sample_metadata_tissue_cell_subtype_uses_enriched_cell_types(workbook, testapp):
    # Tissue and PrimaryCellCulture have no intended_cell_types property at all,
    # so their cell_subtype comes from enriched_cell_types instead.
    row = _get_multi_sample_rows(testapp)['tissue-cultured-treated']
    assert row['cell_subtype'] == 'primary cultured cell'


def test_sample_metadata_mapped_but_unset_columns_are_blank(workbook, testapp):
    # The counterpart to the collection-column assertions on tissue-frozen-basic:
    # this sample sets none of them, and a mapped column with no value must render
    # blank rather than 'placeholder'.
    row = _get_multi_sample_rows(testapp)['cell-line-reference']
    assert row['*biomaterial_provider'] == ''
    assert row['*collection_date'] == ''
    assert row['*geo_loc_name'] == ''
    assert row['*age'] == ''


def test_sample_metadata_rejects_wrong_type(workbook, testapp):
    testapp.get('/matrix-file-set-sample-metadata/?type=SequenceFileSet', status=400)
    testapp.get('/matrix-file-set-sample-metadata/?type=Biosample', status=400)
    testapp.get('/matrix-file-set-sample-metadata/', status=400)


def test_sample_metadata_abstract_biosample_search_resolves(workbook, testapp):
    # Phase B searches the abstract type; every concrete subtype carries 'Biosample'
    # in @type. Asserted directly so a regression here is not misread as an
    # embedding problem.
    r = testapp.get('/search/?type=Biosample&limit=all')
    assert r.json['total'] >= 1
    assert all('Biosample' in hit['@type'] for hit in r.json['@graph'])
