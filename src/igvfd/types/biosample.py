from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    load_schema,
)
from snovault.util import Path
from .base import (
    Item,
    reverse_link_paths,
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
    rev = {
        'plate_based_libraries': ('PlateBasedLibrary', 'samples'),
        'droplet_based_libraries': ('DropletBasedLibrary', 'samples'),
    }
    # A nested Path must follow its parent Path, and the intermediate key must stay
    # in the parent's include list so it survives the parent frame filter.
    # 'title' was dropped from the donors and treatments includes: neither Donor nor
    # Treatment has a title property or a title calculated property, so it was a no-op.
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
        Path('donors', include=['@id', 'aliases', 'taxa', 'sex', 'ethnicity']),
        Path('donors.ethnicity', include=['@id', 'term_name']),
        Path('sample_terms', include=['@id', 'term_name']),
        Path('developmental_stages', include=['@id', 'term_name', 'ontology_source']),
        Path('diseases', include=['@id', 'term_name']),
        Path('enriched_cell_types', include=['@id', 'term_name']),
        Path('genetic_modification', include=['@id', 'strategy']),
        Path('experimental_conditions', include=['@id', 'condition', 'value', 'units', 'text_value']),
        Path('treatments', include=[
            '@id', 'summary', 'ontological_term', 'amount', 'amount_units',
            'lower_bound_duration', 'upper_bound_duration', 'duration_units',
        ]),
        Path('treatments.ontological_term', include=['@id', 'term_name']),
        Path('sources', include=['@id', 'title']),
        # Reverse-link embed. 'libraries' is a calculated property over the rev links
        # declared above; items.linkFrom is what makes it embeddable at all (the
        # mapping generator only treats a path segment as a link when its schema
        # declares linkFrom or linkTo). Embedding it changes the rendered value from
        # a list of @id strings to a list of objects, same as every other embedded
        # link. No embed cycle with Library.samples: each Path expands the target at
        # its object frame, so only the named properties are pulled in.
        Path('libraries', include=['@id', 'CRO_group_identifier']),
    ]

    @calculated_property(
        schema={
            'title': 'Libraries',
            'type': 'array',
            'description': 'Libraries prepared from this biosample.',
            'notSubmittable': True,
            'items': {
                'title': 'Library',
                'type': 'string',
                'linkFrom': 'Library.samples',
            },
        }
    )
    def libraries(self, request):
        uuids = set()
        for rev_key in self.rev:
            uuids.update(self.get_rev_links(rev_key))
        return reverse_link_paths(request, sorted(uuids))


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
