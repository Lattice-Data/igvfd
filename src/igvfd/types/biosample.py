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
    Concrete implementations are Tissue, PrimaryCellCulture, Organoid, and CellLine.
    """
    item_type = 'biosample'
    base_types = ['Biosample'] + Item.base_types
    schema = load_schema('igvfd:schemas/biosample.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
        Path('donors', include=['@id', 'title', 'aliases']),
        Path('sample_terms', include=['@id', 'term_name']),
        Path('developmental_stages', include=['@id', 'term_name', 'ontology_source']),
        Path('treatments', include=['@id', 'title', 'summary']),
        Path('sources', include=['@id', 'title']),
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
    name='primary_cell_cultures',
    properties={
        'title': 'Primary Cell Cultures',
        'description': 'Listing of primary cell culture samples',
    }
)
class PrimaryCellCulture(Biosample):
    item_type = 'primary_cell_culture'
    schema = load_schema('igvfd:schemas/primary_cell_culture.json')
    embedded_with_frame = Biosample.embedded_with_frame

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the primary cell culture sample.',
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
    name='organoids',
    properties={
        'title': 'Organoids',
        'description': 'Listing of organoid samples',
    }
)
class Organoid(Biosample):
    item_type = 'organoid'
    schema = load_schema('igvfd:schemas/organoid.json')
    embedded_with_frame = Biosample.embedded_with_frame + [
        Path('intended_cell_types', include=['@id', 'term_name']),
        Path('origin_cell_types', include=['@id', 'term_name']),
    ]

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the organoid.',
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
    name='cell_lines',
    properties={
        'title': 'Cell Lines',
        'description': 'Listing of cell line samples',
    }
)
class CellLine(Biosample):
    item_type = 'cell_line'
    schema = load_schema('igvfd:schemas/cell_line.json')
    embedded_with_frame = Biosample.embedded_with_frame + [
        Path('host', include=['@id', 'title', 'aliases']),
        Path('host_tissue', include=['@id', 'term_name']),
        Path('intended_cell_types', include=['@id', 'term_name']),
    ]

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the cell line.',
            'notSubmittable': True,
        }
    )
    def summary(self, aliases=None, description=None):
        if aliases:
            return aliases[0]
        if description:
            return description
        return self.uuid
