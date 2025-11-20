from snovault import (
    abstract_collection,
    load_schema,
)
from snovault.util import Path
from .base import (
    Item,
)


@abstract_collection(
    name='libraries',
    properties={
        'title': 'Libraries',
        'description': 'Abstract base class for libraries',
    }
)
class Library(Item):
    """
    Abstract base class for libraries.
    Concrete implementations will include specific library types (e.g., SequencingLibrary).
    """
    item_type = 'library'
    base_types = ['Library'] + Item.base_types
    schema = load_schema('igvfd:schemas/library.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
        Path('samples', include=['@id', 'aliases']),
    ]
