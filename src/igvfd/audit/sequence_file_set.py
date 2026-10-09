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


ILLUMINA_SLOTS = ('read1', 'read2', 'read3', 'index1', 'index2')
CRAM_SLOTS = ('untrimmed_cram', 'trimmed_cram')

RUN_CARDINALITY_BY_SLOTS = {
    frozenset(['read1']): 'single-end',
    frozenset(['read1', 'read2']): 'paired-end',
    frozenset(['read1', 'read2', 'index1']): 'paired-end-with-index',
    frozenset(['read1', 'read2', 'index2']): 'paired-end-with-index',
    frozenset(['read1', 'read2', 'index1', 'index2']): 'paired-end-with-dual-index',
    frozenset(['read1', 'read2', 'read3']): 'triplet',
}


def audit_sequence_file_set_inconsistent_run_cardinality(value, system):
    '''
    [
        {
            "audit_description": "Sequence file sets are expected to have a run cardinality that matches their linked read and index files, and sets with CRAM files are expected to be single-end.",
            "audit_category": "inconsistent run cardinality",
            "audit_level": "ERROR"
        }
    ]
    '''
    populated = [slot for slot in ILLUMINA_SLOTS + CRAM_SLOTS if value.get(slot)]
    if not populated:
        return
    run_cardinality = value.get('run_cardinality')
    if all(slot in CRAM_SLOTS for slot in populated):
        # Ultima Genomics CRAM files hold every read, so the run is single-end.
        expected = 'single-end'
    else:
        expected = RUN_CARDINALITY_BY_SLOTS.get(frozenset(populated))
    if expected == run_cardinality:
        return
    audit_message = get_audit_message(audit_sequence_file_set_inconsistent_run_cardinality)
    object_type = space_in_words(value['@type'][0]).capitalize()
    set_id = value['@id']
    slots = ', '.join(f'`{slot}`' for slot in populated)
    if expected:
        expectation = f'which corresponds to `run_cardinality` `{expected}`'
    else:
        expectation = 'which does not correspond to any `run_cardinality`'
    detail = (
        f'{object_type} {audit_link(path_to_text(set_id), set_id)} '
        f'has `run_cardinality` `{run_cardinality}` but links {slots}, {expectation}.'
    )
    yield AuditFailure(
        audit_message.get('audit_category', ''),
        f'{detail} {audit_message.get("audit_description", "")}',
        level=audit_message.get('audit_level', ''),
    )


function_dispatcher_sequence_file_set_object = {
    'audit_sequence_file_set_inconsistent_run_cardinality': audit_sequence_file_set_inconsistent_run_cardinality,
}


@audit_checker('SequenceFileSet', frame='object')
def audit_sequence_file_set_object_dispatcher(value, system):
    for function_name in function_dispatcher_sequence_file_set_object:
        for failure in function_dispatcher_sequence_file_set_object[function_name](value, system):
            yield failure
