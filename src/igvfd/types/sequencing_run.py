from snovault import (
    collection,
    calculated_property,
    load_schema,
)
from snovault.util import Path
from .base import (
    Item,
)


@collection(
    name='sequencing_runs',
    properties={
        'title': 'Sequencing Runs',
        'description': 'Listing of sequencing runs',
    }
)
class SequencingRun(Item):
    '''
    Sequencing run representing a logical grouping of sequence files.
    Used primarily for Illumina platforms that generate multiple FASTQ files
    (reads and indices) that need to be grouped together.
    '''
    item_type = 'sequencing_run'
    schema = load_schema('igvfd:schemas/sequencing_run.json')
    embedded_with_frame = [
        Path('lab', include=['@id', 'title']),
        Path('submitted_by', include=['@id', 'title']),
        Path('read1', include=['@id', 'aliases', 'file_format']),
        Path('read2', include=['@id', 'aliases', 'file_format']),
        Path('read3', include=['@id', 'aliases', 'file_format']),
        Path('index1', include=['@id', 'aliases', 'file_format']),
        Path('index2', include=['@id', 'aliases', 'file_format']),
    ]

    @calculated_property(
        schema={
            'title': 'Summary',
            'type': 'string',
            'description': 'A summary of the sequencing run.',
            'notSubmittable': True,
        }
    )
    def summary(self, aliases=None, run_cardinality=None):
        if aliases:
            return aliases[0]
        if run_cardinality:
            return f'{run_cardinality} run ({self.uuid[:8]})'
        return self.uuid
