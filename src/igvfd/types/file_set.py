from snovault import (
    abstract_collection,
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
