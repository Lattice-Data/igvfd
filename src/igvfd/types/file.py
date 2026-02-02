from snovault import (
    abstract_collection,
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
