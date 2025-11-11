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
    name='donors',
    properties={
        'title': 'Donors',
        'description': 'Abstract base class for donors',
    }
)
class Donor(Item):
    """
    Abstract base class for donors.
    Concrete implementations are HumanDonor and NonHumanDonor.
    """
    item_type = 'donor'
    base_types = ['Donor'] + Item.base_types
    schema = load_schema('igvfd:schemas/donor.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
    ]


@collection(
    name='human_donors',
    properties={
        'title': 'Human Donors',
        'description': 'Listing of human research subjects and donors',
    }
)
class HumanDonor(Donor):
    item_type = 'human_donor'
    schema = load_schema('igvfd:schemas/human_donor.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
    ]

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the human donor.',
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
    name='non_human_donors',
    properties={
        'title': 'Non Human Donors',
        'description': 'Listing of non human donors.',
    }
)
class NonHumanDonor(Donor):
    item_type = 'non_human_donor'
    schema = load_schema('igvfd:schemas/non_human_donor.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
    ]

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the non human donor.',
            'notSubmittable': True,
        }
    )
    def summary(self, aliases=None, description=None):
        if aliases:
            return aliases[0]
        if description:
            return description
        return self.uuid
