from collections import OrderedDict

MATRIX_FILE_SET_METADATA_ALLOWED_TYPES = ['MatrixFileSet']

# Typed file-link properties the engine flattens into one file iterable.
MATRIX_FILE_SET_FILE_LINK_FIELDS = [
    'raw_matrix_files',
    'processed_matrix_files',
]

# Column header -> field path. 'files.' prefix marks file-level columns.
# Restricted to already-embedded fields (no new embedding this ticket).
FROM_MATRIX_FILE_SET_FIELDS = OrderedDict([
    ('File ID', ['files.@id']),
    ('File aliases', ['files.aliases']),
    ('File format', ['files.file_format']),
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

METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING = [
    ('WARNING', 'Audit WARNING'),
    ('NOT_COMPLIANT', 'Audit NOT_COMPLIANT'),
    ('ERROR', 'Audit ERROR'),
]

BOOLEAN_MAP = {
    'true': True,
    'false': False
}
