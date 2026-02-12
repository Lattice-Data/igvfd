from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    load_schema,
)
from snovault.util import Path
from .base import (
    Item,
)


@abstract_collection(
    name='files',
    properties={
        'title': 'Files',
        'description': 'Abstract base class for files',
    }
)
class File(Item):
    """
    Abstract base class for files.
    Concrete implementations will define specific file types.
    """
    item_type = 'file'
    base_types = ['File'] + Item.base_types
    schema = load_schema('igvfd:schemas/file.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
    ]


@collection(
    name='sequence_files',
    properties={
        'title': 'Sequence Files',
        'description': 'Listing of sequence files',
    }
)
class SequenceFile(File):
    item_type = 'sequence_file'
    schema = load_schema('igvfd:schemas/sequence_file.json')
    embedded_with_frame = File.embedded_with_frame

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the sequence file.',
            'notSubmittable': True,
        }
    )
    def summary(self, aliases=None, description=None):
        if aliases:
            return aliases[0]
        if description:
            return description
        return self.uuid


@collection(
    name='tabular_files',
    properties={
        'title': 'Tabular Files',
        'description': 'Listing of tabular files',
    }
)
class TabularFile(File):
    item_type = 'tabular_file'
    schema = load_schema('igvfd:schemas/tabular_file.json')
    embedded_with_frame = File.embedded_with_frame

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the tabular file.',
            'notSubmittable': True,
        }
    )
    def summary(self, aliases=None, description=None):
        if aliases:
            return aliases[0]
        if description:
            return description
        return self.uuid


@collection(
    name='raw_matrix_files',
    properties={
        'title': 'Raw Matrix Files',
        'description': 'Listing of raw matrix files',
    }
)
class RawMatrixFile(File):
    item_type = 'raw_matrix_file'
    schema = load_schema('igvfd:schemas/raw_matrix_file.json')
    embedded_with_frame = File.embedded_with_frame

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the raw matrix file.',
            'notSubmittable': True,
        }
    )
    def summary(self, aliases=None, description=None):
        if aliases:
            return aliases[0]
        if description:
            return description
        return self.uuid


@collection(
    name='processed_matrix_files',
    properties={
        'title': 'Processed Matrix Files',
        'description': 'Listing of processed matrix files',
    }
)
class ProcessedMatrixFile(File):
    item_type = 'processed_matrix_file'
    schema = load_schema('igvfd:schemas/processed_matrix_file.json')
    embedded_with_frame = File.embedded_with_frame

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the processed matrix file.',
            'notSubmittable': True,
        }
    )
    def summary(self, aliases=None, description=None):
        if aliases:
            return aliases[0]
        if description:
            return description
        return self.uuid
