from snovault import (
    AuditFailure,
    audit_checker,
)

from .formatter import (
    audit_link,
    get_audit_message,
    path_to_text,
    space_in_words,
)

# NCBITaxon term_ids of the non human donor species that can be hermaphrodites.
HERMAPHRODITIC_TAXA_TERM_IDS = {
    'NCBITaxon:10201',  # Beroe ovata
    'NCBITaxon:6526',  # Biomphalaria glabrata
    'NCBITaxon:7719',  # Ciona intestinalis
    'NCBITaxon:216498',  # Hydroides elegans
    'NCBITaxon:27923',  # Mnemiopsis leidyi
    'NCBITaxon:7769',  # Myxine glutinosa
    'NCBITaxon:27933',  # Sycon ciliatum
}


def audit_non_human_donor_hermaphrodite_sex(value, system):
    '''
    [
        {
            "audit_description": "Non human donors are expected to have sex hermaphrodite only when their taxa is a hermaphroditic species.",
            "audit_category": "inconsistent sex",
            "audit_level": "ERROR"
        }
    ]
    '''
    if value.get('sex') != 'hermaphrodite':
        return
    taxa = value.get('taxa')
    if not isinstance(taxa, dict):
        return
    if taxa.get('term_id') in HERMAPHRODITIC_TAXA_TERM_IDS:
        return
    audit_message = get_audit_message(audit_non_human_donor_hermaphrodite_sex)
    object_type = space_in_words(value['@type'][0]).capitalize()
    donor_id = value['@id']
    taxa_id = taxa.get('@id', '')
    detail = (
        f'{object_type} {audit_link(path_to_text(donor_id), donor_id)} '
        f'has `sex` `hermaphrodite`, but its `taxa` {audit_link(path_to_text(taxa_id), taxa_id)} '
        f'is not a hermaphroditic species.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


function_dispatcher_non_human_donor_embedded = {
    'audit_non_human_donor_hermaphrodite_sex': audit_non_human_donor_hermaphrodite_sex,
}


@audit_checker('NonHumanDonor', frame='embedded')
def audit_non_human_donor_embedded_dispatcher(value, system):
    for function_name in function_dispatcher_non_human_donor_embedded:
        for failure in function_dispatcher_non_human_donor_embedded[function_name](value, system):
            yield failure
