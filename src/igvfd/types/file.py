from pyramid.traversal import traverse
from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    load_schema,
)
from snovault.util import Path
from igvfd.sra_file_names import (
    READ_SLOTS,
    set_file_names,
)
from .base import (
    Item,
    reverse_link_paths,
)


def read_slot_references(request, item):
    '''(slot, set) for each read slot of a non-deleted SequenceFileSet that names item.'''
    references = []
    for slot in READ_SLOTS:
        for set_uuid in item.get_rev_links(slot):
            # skip_calculated: a mate's own sra_file_names would embed this file again
            file_set = request.embed('/', str(set_uuid), '@@object?skip_calculated=true')
            if file_set.get('status') != 'deleted':
                references.append((slot, file_set))
    return references


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
    rev = {
        'read1': ('SequenceFileSet', 'read1'),
        'read2': ('SequenceFileSet', 'read2'),
        'read3': ('SequenceFileSet', 'read3'),
        'index1': ('SequenceFileSet', 'index1'),
        'index2': ('SequenceFileSet', 'index2'),
        'untrimmed_cram': ('SequenceFileSet', 'untrimmed_cram'),
        'trimmed_cram': ('SequenceFileSet', 'trimmed_cram'),
    }

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
        uuids = set()
        for rev_key in self.rev:
            uuids.update(self.get_rev_links(rev_key))
        return reverse_link_paths(request, sorted(uuids))

    @calculated_property(
        schema={
            'title': 'SRA File Names',
            'type': 'array',
            'description': 'Names under which the reads of this file are submitted to SRA: the '
                           'file name itself, or the names of its chunks once a file of its '
                           'sequence file set reaches the 100 GB SRA limit.',
            'items': {
                'title': 'SRA File Name',
                'type': 'string',
            },
            'notSubmittable': True,
        }
    )
    def sra_file_names(self, request, file_format=None):
        # Absent wherever fastq_chunker would refuse the set, including when this
        # file or any mate sits in the read slots of more than one non-deleted set.
        if file_format != 'fastq':
            return None
        references = read_slot_references(request, self)
        if len(references) != 1:
            return None
        own_slot, file_set = references[0]
        mates = {}
        for slot in READ_SLOTS:
            if slot not in file_set:
                continue
            mate = request.embed(file_set[slot], '@@object?skip_calculated=true')
            # skip_calculated objects carry no uuid; resolve the mate by its path
            mate_item = traverse(request.root, file_set[slot])['context']
            if len(read_slot_references(request, mate_item)) != 1:
                return None
            mates[slot] = mate
        names = set_file_names(mates)
        return None if names is None else names[own_slot]


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

    def unique_keys(self, properties):
        keys = super(TabularFile, self).unique_keys(properties)
        if properties.get('status') != 'deleted' and 'guides_signature' in properties:
            keys.setdefault('alias', []).append(properties['guides_signature'])
        return keys

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
    rev = {
        'matrix_file_sets': ('MatrixFileSet', 'raw_matrix_files'),
    }

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
        uuids = self.get_rev_links('matrix_file_sets')
        return reverse_link_paths(request, sorted(uuids))


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
    rev = {
        'matrix_file_sets': ('MatrixFileSet', 'processed_matrix_files'),
    }

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
        uuids = self.get_rev_links('matrix_file_sets')
        return reverse_link_paths(request, sorted(uuids))
