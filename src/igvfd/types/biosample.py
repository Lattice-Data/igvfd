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
    name='biosamples',
    properties={
        'title': 'Biosamples',
        'description': 'Abstract base class for biosamples',
    }
)
class Biosample(Item):
    """
    Abstract base class for biosamples.
    Concrete implementations are Tissue, InVivoSystem, and InVitroSystem.
    """
    item_type = 'biosample'
    base_types = ['Biosample'] + Item.base_types
    schema = load_schema('igvfd:schemas/biosample.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
        Path('donors', include=['@id', 'title', 'aliases']),
        Path('sample_terms', include=['@id', 'term_name']),
    ]


@collection(
    name='tissues',
    properties={
        'title': 'Tissues',
        'description': 'Listing of tissue samples',
    }
)
class Tissue(Biosample):
    item_type = 'tissue'
    schema = load_schema('igvfd:schemas/tissue.json')
    embedded_with_frame = Biosample.embedded_with_frame

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the tissue sample.',
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
    name='in_vivo_systems',
    properties={
        'title': 'In Vivo Systems',
        'description': 'Listing of in vivo biological systems',
    }
)
class InVivoSystem(Biosample):
    item_type = 'in_vivo_system'
    schema = load_schema('igvfd:schemas/in_vivo_system.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
        Path('donors', include=['@id', 'title', 'aliases']),
        Path('sample_terms', include=['@id', 'term_name']),
        Path('host', include=['@id', 'title', 'aliases']),
    ]

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the in vivo system.',
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
    name='in_vitro_systems',
    properties={
        'title': 'In Vitro Systems',
        'description': 'Listing of in vitro biological systems',
    }
)
class InVitroSystem(Biosample):
    item_type = 'in_vitro_system'
    schema = load_schema('igvfd:schemas/in_vitro_system.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
        Path('donors', include=['@id', 'title', 'aliases']),
        Path('sample_terms', include=['@id', 'term_name']),
    ]

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the in vitro system.',
            'notSubmittable': True,
        }
    )
    def summary(self, aliases=None, description=None):
        if aliases:
            return aliases[0]
        if description:
            return description
        return self.uuid
