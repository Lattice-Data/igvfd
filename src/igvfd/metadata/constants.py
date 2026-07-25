from collections import OrderedDict

MATRIX_FILE_SET_METADATA_ALLOWED_TYPES = ['MatrixFileSet']

MATRIX_FILE_SET_FILE_LINK_FIELDS = [
    'raw_matrix_files',
    'processed_matrix_files',
]

# Columns populated from each embedded matrix file object.
FROM_MATRIX_FILE_COLUMNS = OrderedDict([
    ('File ID', ['@id']),
    ('File aliases', ['aliases']),
    ('File format', ['file_format']),
])

# Columns populated from the MatrixFileSet object.
FROM_MATRIX_FILE_SET_COLUMNS = OrderedDict([
    ('File set ID', ['@id']),
    ('File set type', ['@type']),
    ('File set aliases', ['aliases']),
    ('File set summary', ['summary']),
    ('File set status', ['status']),
    ('File set description', ['description']),
    ('File set lab', ['lab.title']),
    ('Submitted by', ['submitted_by.title']),
    ('Creation timestamp', ['creation_timestamp']),
])

FROM_MATRIX_FILE_SET_FIELDS = OrderedDict()
FROM_MATRIX_FILE_SET_FIELDS.update(FROM_MATRIX_FILE_COLUMNS)
FROM_MATRIX_FILE_SET_FIELDS.update(FROM_MATRIX_FILE_SET_COLUMNS)

MATRIX_FILE_SET_SAMPLE_METADATA_ALLOWED_TYPES = ['MatrixFileSet']

# Emitted for columns that have no derivable Lattice source, so a submitter can see
# which cells still need to be filled in by hand. Distinct from an empty cell, which
# means the column IS mapped but this row has no value for it.
SAMPLE_METADATA_PLACEHOLDER = 'placeholder'

# Multi-valued sample cells are joined with '; ', matching the GEO flattener in
# lattice-tools (DB2Flattener._join_unique), not the ', ' used by the file report.
SAMPLE_VALUE_SEPARATOR = '; '

# Concrete Biosample types. Several target columns are fed by the same Lattice
# property but belong to a different output column depending on the row's type.
SAMPLE_TYPE_LABELS = OrderedDict([
    ('Tissue', 'tissue'),
    ('PrimaryCellCulture', 'primary cell culture'),
    ('Organoid', 'organoid'),
    ('CellLine', 'cell line'),
])

# Types whose intended_cell_types feed cell_subtype; the rest use enriched_cell_types.
INTENDED_CELL_TYPE_SAMPLE_TYPES = ('CellLine', 'Organoid')

# Top-level fields requested for each Biosample row. Whole embedded objects are
# requested (as the file report does for matrix files) so nested paths ride along.
BIOSAMPLE_METADATA_FIELDS = [
    '@id',
    '@type',
    'aliases',
    'description',
    'date_obtained',
    'collection_geographical_location',
    'multiplexing_barcodes',
    'donors',
    'sample_terms',
    'developmental_stages',
    'diseases',
    'enriched_cell_types',
    'intended_cell_types',
    'genetic_modification',
    'experimental_conditions',
    'treatments',
    'sources',
    'libraries',
    'audit',
]

# One row per unique Biosample. Column specs:
#   {'placeholder': True}      -> constant SAMPLE_METADATA_PLACEHOLDER
#   {'path': 'a.b'}            -> dotted path on the row object, separator-joined
#   {'clean_alias': True}      -> strip the 'lab:' prefix from each value
#   {'types': (...)}           -> only rendered for these concrete @types, else blank
#   {'render': 'name'}         -> custom renderer, needed where a cell composes
#                                 several fields of the SAME object (joining them
#                                 with a path list would pair values across objects)
FROM_BIOSAMPLE_COLUMNS = OrderedDict([
    ('*sample_name', {'path': 'aliases', 'clean_alias': True}),
    ('sample_title', {'placeholder': True}),
    ('bioproject_accession', {'placeholder': True}),
    ('library_id', {'render': 'library_id'}),
    ('*organism', {'path': 'donors.taxa'}),
    ('*isolate', {'placeholder': True}),
    ('*age', {'path': 'developmental_stages.term_name'}),
    ('*biomaterial_provider', {'path': 'sources.title'}),
    ('*collection_date', {'path': 'date_obtained'}),
    ('*geo_loc_name', {'path': 'collection_geographical_location'}),
    ('*sex', {'path': 'donors.sex'}),
    ('*tissue', {'path': 'sample_terms.term_name', 'types': ('Tissue', 'Organoid')}),
    ('cell_line', {'path': 'sample_terms.term_name', 'types': ('CellLine',)}),
    ('cell_subtype', {'render': 'cell_subtype'}),
    ('samples', {'placeholder': True}),
    ('sample: sample_probe_barcode', {'path': 'multiplexing_barcodes'}),
    ('perturbation_strategy', {'path': 'genetic_modification.strategy'}),
    ('perturbation_system_type', {'placeholder': True}),
    ('experimental_perturbation_factors', {'render': 'perturbation_factors'}),
    ('experimental_perturbation_timepoint', {'render': 'perturbation_timepoint'}),
    ('ethnicity', {'path': 'donors.ethnicity.term_name'}),
    ('health_state', {'path': 'diseases.term_name'}),
    ('karyotype', {'placeholder': True}),
    ('phenotype', {'placeholder': True}),
    ('population', {'placeholder': True}),
    ('race', {'placeholder': True}),
    ('sample_type', {'render': 'sample_type'}),
    ('treatment', {'render': 'treatment'}),
    ('description', {'path': 'description'}),
])

METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING = [
    ('WARNING', 'Audit WARNING'),
    ('NOT_COMPLIANT', 'Audit NOT_COMPLIANT'),
    ('ERROR', 'Audit ERROR'),
]

BOOLEAN_MAP = {
    'true': True,
    'false': False
}
