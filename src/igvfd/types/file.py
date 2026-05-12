from snovault import (
    CONNECTION,
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


def _reverse_link_paths(request, uuids):
    return [request.embed('/', str(uuid), '@@object')['@id'] for uuid in uuids]


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

    @calculated_property(
        schema={
            'title': 'Sequence File Sets',
            'type': 'array',
            'description': 'Sequence file sets that include this sequence file.',
            'items': {
                'title': 'Sequence File Set',
                'type': 'string',
            },
            'notSubmittable': True,
        }
    )
    def sequence_file_sets(self, request):
        connection = self.registry[CONNECTION]
        file_set_fields = (
            'read1',
            'read2',
            'read3',
            'index1',
            'index2',
            'untrimmed_cram',
            'trimmed_cram',
        )
        uuids = set()
        for field in file_set_fields:
            uuids.update(connection.get_rev_links(self.model, field, 'SequenceFileSet'))
        return _reverse_link_paths(request, sorted(uuids))


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

    @calculated_property(
        schema={
            'title': 'Matrix File Sets',
            'type': 'array',
            'description': 'Matrix file sets that include this raw matrix file.',
            'notSubmittable': True,
            'items': {
                'title': 'Matrix File Set',
                'type': 'string',
                'linkFrom': 'MatrixFileSet.raw_matrix_files',
            },
        }
    )
    def matrix_file_sets(self, request):
        uuids = self.registry[CONNECTION].get_rev_links(self.model, 'raw_matrix_files', 'MatrixFileSet')
        return _reverse_link_paths(request, sorted(uuids))


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

    @calculated_property(
        schema={
            'title': 'Matrix File Sets',
            'type': 'array',
            'description': 'Matrix file sets that include this processed matrix file.',
            'notSubmittable': True,
            'items': {
                'title': 'Matrix File Set',
                'type': 'string',
                'linkFrom': 'MatrixFileSet.processed_matrix_files',
            },
        }
    )
    def matrix_file_sets(self, request):
        uuids = self.registry[CONNECTION].get_rev_links(self.model, 'processed_matrix_files', 'MatrixFileSet')
        return _reverse_link_paths(request, sorted(uuids))
