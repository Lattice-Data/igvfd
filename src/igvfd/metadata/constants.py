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

METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING = [
    ('WARNING', 'Audit WARNING'),
    ('NOT_COMPLIANT', 'Audit NOT_COMPLIANT'),
    ('ERROR', 'Audit ERROR'),
]

BOOLEAN_MAP = {
    'true': True,
    'false': False
}
