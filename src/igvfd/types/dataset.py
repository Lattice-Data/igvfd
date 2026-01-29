from snovault import (
    abstract_collection,
    load_schema,
)
from snovault.util import Path

from .base import Item


@abstract_collection(
    name='datasets',
    properties={
        'title': 'Datasets',
        'description': 'Abstract base class for datasets',
    }
)
class Dataset(Item):
    """Abstract base class for datasets."""

    item_type = 'dataset'
    base_types = ['Dataset'] + Item.base_types
    schema = load_schema('igvfd:schemas/dataset.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
    ]
