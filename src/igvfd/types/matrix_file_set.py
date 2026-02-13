from snovault import (
    collection,
    calculated_property,
    load_schema,
)
from snovault.util import Path
from .file_set import (
    FileSet,
)


@collection(
    name='matrix_file_sets',
    properties={
        'title': 'Matrix File Sets',
        'description': 'Listing of matrix file sets',
    }
)
class MatrixFileSet(FileSet):
    '''
    A set of matrix files produced from processing sequence data.
    '''
    item_type = 'matrix_file_set'
    schema = load_schema('igvfd:schemas/matrix_file_set.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
        Path('raw_matrix_files', include=['@id', 'aliases', 'file_format']),
        Path('processed_matrix_files', include=['@id', 'aliases', 'file_format']),
        Path('source_sequence_file_sets', include=['@id', 'aliases']),
    ]

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the matrix file set.',
            'notSubmittable': True,
        }
    )
    def summary(self, aliases=None, description=None):
        if aliases:
            return aliases[0]
        if description:
            return description
        return self.uuid
