from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    load_schema,
)
from snovault.util import Path

from .base import Item


@abstract_collection(
    name='file_sets',
    properties={
        'title': 'File Sets',
        'description': 'Abstract base class for file sets',
    }
)
class FileSet(Item):
    """
    Abstract base class for file sets.
    Concrete implementations are SequenceFileSet and MatrixFileSet.
    """
    item_type = 'file_set'
    base_types = ['FileSet'] + Item.base_types
    schema = load_schema('igvfd:schemas/file_set.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
    ]


@collection(
    name='sequence_file_sets',
    properties={
        'title': 'Sequence File Sets',
        'description': 'Listing of sequence file sets',
    }
)
class SequenceFileSet(FileSet):
    '''
    A set of sequence files produced from sequencing a library.
    Supports both Illumina multi-file layouts (read1/read2/read3/index1/index2)
    and single-file platforms like Ultima Genomics (untrimmed_cram/trimmed_cram).
    '''
    item_type = 'sequence_file_set'
    schema = load_schema('igvfd:schemas/sequence_file_set.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
        Path('library', include=['@id', 'aliases']),
        Path('read1', include=['@id', 'aliases', 'file_format']),
        Path('read2', include=['@id', 'aliases', 'file_format']),
        Path('read3', include=['@id', 'aliases', 'file_format']),
        Path('index1', include=['@id', 'aliases', 'file_format']),
        Path('index2', include=['@id', 'aliases', 'file_format']),
        Path('untrimmed_cram', include=['@id', 'aliases', 'file_format']),
        Path('trimmed_cram', include=['@id', 'aliases', 'file_format']),
    ]

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the sequence file set.',
            'notSubmittable': True,
        }
    )
    def summary(self, aliases=None, run_cardinality=None):
        if aliases:
            return aliases[0]
        if run_cardinality:
            return f'{run_cardinality} file set ({str(self.uuid)[:8]})'
        return self.uuid


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
        Path('raw_matrix_files', include=['@id', 'aliases', 'file_format', 'observation_count']),
        Path('processed_matrix_files', include=['@id', 'aliases', 'file_format', 'observation_count']),
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
