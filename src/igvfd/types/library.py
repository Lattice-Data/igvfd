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
    name='libraries',
    properties={
        'title': 'Libraries',
        'description': 'Abstract base class for libraries',
    }
)
class Library(Item):
    """
    Abstract base class for libraries.
    Concrete implementations are PlateBasedLibrary and DropletBasedLibrary.
    """
    item_type = 'library'
    base_types = ['Library'] + Item.base_types
    schema = load_schema('igvfd:schemas/library.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
        Path('samples', include=['@id', 'aliases']),
    ]


@collection(
    name='plate_based_libraries',
    properties={
        'title': 'Plate Based Libraries',
        'description': 'Listing of plate-based single cell libraries',
    }
)
class PlateBasedLibrary(Library):
    item_type = 'plate_based_library'
    schema = load_schema('igvfd:schemas/plate_based_library.json')
    embedded_with_frame = Library.embedded_with_frame

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the plate-based library.',
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
    name='droplet_based_libraries',
    properties={
        'title': 'Droplet Based Libraries',
        'description': 'Listing of droplet-based single cell libraries',
    }
)
class DropletBasedLibrary(Library):
    item_type = 'droplet_based_library'
    schema = load_schema('igvfd:schemas/droplet_based_library.json')
    embedded_with_frame = Library.embedded_with_frame

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the droplet-based library.',
            'notSubmittable': True,
        }
    )
    def summary(self, aliases=None, description=None):
        if aliases:
            return aliases[0]
        if description:
            return description
        return self.uuid
