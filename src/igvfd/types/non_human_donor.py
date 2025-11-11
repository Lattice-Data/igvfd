from snovault import (
    collection,
    load_schema,
    calculated_property,
)
from snovault.util import Path
from .base import (
    Item,
)


@collection(
    name='non_human_donors',
    properties={
        'title': 'Non Human Donors',
        'description': 'Listing of non human donors.',
    }
)
class NonHumanDonor(Item):
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

