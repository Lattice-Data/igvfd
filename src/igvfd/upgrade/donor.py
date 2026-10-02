from snovault import CONNECTION
from snovault.upgrader import upgrade_step

from .aliases import preserve_invalid_aliases

_CXG_PLACEHOLDER = 'placeholder cxg donor id'

# The NCBITaxon term_id for each taxa enum value the 3 -> 4 steps replace with a link to
# its ControlledTerm. The steps are historical once released, so do not edit this to
# track a later schema change.
TAXA_TERM_IDS = {
    'Alligator mississippiensis': 'NCBITaxon:8496',
    'Anolis carolinensis': 'NCBITaxon:28377',
    'Beroe ovata': 'NCBITaxon:10201',
    'Biomphalaria glabrata': 'NCBITaxon:6526',
    'Chrysemys picta bellii': 'NCBITaxon:8478',
    'Ciona intestinalis': 'NCBITaxon:7719',
    'Coturnix japonica': 'NCBITaxon:93934',
    'Danio rerio': 'NCBITaxon:7955',
    'Euprymna berryi': 'NCBITaxon:153281',
    'Homo sapiens': 'NCBITaxon:9606',
    'Hydroides elegans': 'NCBITaxon:216498',
    'Leucoraja erinaceus': 'NCBITaxon:7782',
    'Limulus polyphemus': 'NCBITaxon:6850',
    'Littorina littorea': 'NCBITaxon:31216',
    'Mnemiopsis leidyi': 'NCBITaxon:27923',
    'Monodelphis domestica': 'NCBITaxon:13616',
    'Mus musculus': 'NCBITaxon:10090',
    'Myxine glutinosa': 'NCBITaxon:7769',
    'Nematostella vectensis': 'NCBITaxon:45351',
    'Nothobranchius furzeri': 'NCBITaxon:105023',
    'Octopus bimaculoides': 'NCBITaxon:37653',
    'Parhyale hawaiensis': 'NCBITaxon:317513',
    'Patiria miniata': 'NCBITaxon:46514',
    'Petromyzon marinus': 'NCBITaxon:7757',
    'Platynereis megalops': 'NCBITaxon:3269935',
    'Ranitomeya imitator': 'NCBITaxon:111125',
    'Saccoglossus kowalevskii': 'NCBITaxon:10224',
    'Sclerodactyla briareus': 'NCBITaxon:7710',
    'Sycon ciliatum': 'NCBITaxon:27933',
    'Turritopsis dohrnii': 'NCBITaxon:308579',
    'Xenopus tropicalis': 'NCBITaxon:8364',
}


@upgrade_step('human_donor', '1', '2')
def human_donor_1_2(value, system):
    if 'cxg_donor_id' not in value or value['cxg_donor_id'] in (None, ''):
        value['cxg_donor_id'] = _CXG_PLACEHOLDER


@upgrade_step('non_human_donor', '1', '2')
def non_human_donor_1_2(value, system):
    if 'cxg_donor_id' not in value or value['cxg_donor_id'] in (None, ''):
        value['cxg_donor_id'] = _CXG_PLACEHOLDER


@upgrade_step('human_donor', '2', '3')
def human_donor_2_3(value, system):
    preserve_invalid_aliases(value)


@upgrade_step('non_human_donor', '2', '3')
def non_human_donor_2_3(value, system):
    preserve_invalid_aliases(value)


def link_taxa_to_controlled_term(value, system):
    """Replace the taxa enum value with the uuid of its NCBITaxon ControlledTerm.

    Raises when the term is not in the database, so the object keeps its old version
    rather than losing its taxa.
    """
    if 'taxa' not in value:
        return
    taxa = value['taxa']
    term_id = TAXA_TERM_IDS[taxa]
    connection = system['registry'][CONNECTION]
    term = connection.get_by_unique_key('controlled_term:term_id', term_id)
    if term is None:
        raise ValueError(f'No ControlledTerm {term_id} to link taxa {taxa!r} to.')
    value['taxa'] = str(term.uuid)


@upgrade_step('human_donor', '3', '4')
def human_donor_3_4(value, system):
    link_taxa_to_controlled_term(value, system)


@upgrade_step('non_human_donor', '3', '4')
def non_human_donor_3_4(value, system):
    link_taxa_to_controlled_term(value, system)
