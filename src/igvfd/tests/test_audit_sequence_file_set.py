import pytest

from igvfd.audit.sequence_file_set import (
    audit_sequence_file_set_duplicate_sequence_file,
    audit_sequence_file_set_inconsistent_run_cardinality,
)


CATEGORY = 'inconsistent run cardinality'
DUPLICATE_CATEGORY = 'duplicate sequence file'


def _audit_errors(res):
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    return errors_list


def _value(run_cardinality, slots):
    value = {
        '@type': ['SequenceFileSet'],
        '@id': '/sequence-file-sets/b2a1f0d2-0000-4000-8000-000000000001/',
        'run_cardinality': run_cardinality,
    }
    for slot in slots:
        value[slot] = f'/sequence-files/IGVFDTEST{slot}/'
    return value


@pytest.mark.parametrize('run_cardinality,slots', [
    ('single-end', ['read1']),
    ('paired-end', ['read1', 'read2']),
    ('paired-end-with-index', ['read1', 'read2', 'index1']),
    ('paired-end-with-index', ['read1', 'read2', 'index2']),
    ('paired-end-with-dual-index', ['read1', 'read2', 'index1', 'index2']),
    ('triplet', ['read1', 'read2', 'read3']),
])
def test_consistent_run_cardinality_no_audit(run_cardinality, slots):
    failures = list(audit_sequence_file_set_inconsistent_run_cardinality(
        _value(run_cardinality, slots), {}))
    assert failures == []


@pytest.mark.parametrize('run_cardinality,slots,expected', [
    ('single-end', ['read1', 'read2'], 'paired-end'),
    ('paired-end', ['read1'], 'single-end'),
    ('paired-end', ['read1', 'read2', 'index1'], 'paired-end-with-index'),
    ('paired-end', ['read1', 'read2', 'read3'], 'triplet'),
    ('paired-end-with-index', ['read1', 'read2', 'index1', 'index2'], 'paired-end-with-dual-index'),
    ('paired-end-with-dual-index', ['read1', 'read2', 'index1'], 'paired-end-with-index'),
    ('triplet', ['read1', 'read2'], 'paired-end'),
])
def test_inconsistent_run_cardinality_audit(run_cardinality, slots, expected):
    failures = list(audit_sequence_file_set_inconsistent_run_cardinality(
        _value(run_cardinality, slots), {}))
    assert len(failures) == 1
    assert failures[0].category == CATEGORY
    assert failures[0].__json__()['level_name'] == 'ERROR'
    assert f'corresponds to `run_cardinality` `{expected}`' in failures[0].detail


@pytest.mark.parametrize('run_cardinality,slots', [
    ('triplet', ['read1', 'read2', 'read3', 'index1']),
    ('single-end', ['read1', 'index1']),
    ('paired-end', ['read2']),
])
def test_unrecognized_slot_combination_audit(run_cardinality, slots):
    failures = list(audit_sequence_file_set_inconsistent_run_cardinality(
        _value(run_cardinality, slots), {}))
    assert len(failures) == 1
    assert failures[0].category == CATEGORY
    assert 'does not correspond to any `run_cardinality`' in failures[0].detail


@pytest.mark.parametrize('slots', [
    ['untrimmed_cram'],
    ['trimmed_cram'],
    ['untrimmed_cram', 'trimmed_cram'],
])
def test_cram_single_end_no_audit(slots):
    failures = list(audit_sequence_file_set_inconsistent_run_cardinality(
        _value('single-end', slots), {}))
    assert failures == []


@pytest.mark.parametrize('run_cardinality', [
    'paired-end',
    'paired-end-with-index',
    'paired-end-with-dual-index',
    'triplet',
])
@pytest.mark.parametrize('slots', [
    ['untrimmed_cram'],
    ['trimmed_cram'],
])
def test_cram_not_single_end_audit(run_cardinality, slots):
    failures = list(audit_sequence_file_set_inconsistent_run_cardinality(
        _value(run_cardinality, slots), {}))
    assert len(failures) == 1
    assert failures[0].category == CATEGORY
    assert failures[0].__json__()['level_name'] == 'ERROR'
    assert 'corresponds to `run_cardinality` `single-end`' in failures[0].detail


def test_cram_mixed_with_reads_audit():
    failures = list(audit_sequence_file_set_inconsistent_run_cardinality(
        _value('single-end', ['read1', 'untrimmed_cram']), {}))
    assert len(failures) == 1
    assert 'does not correspond to any `run_cardinality`' in failures[0].detail


def test_no_linked_files_no_audit():
    failures = list(audit_sequence_file_set_inconsistent_run_cardinality(
        _value('paired-end', []), {}))
    assert failures == []


def test_sequence_file_set_fixtures_clean(
    indexer_testapp,
    sequence_file_set_illumina_single_end,
    sequence_file_set_illumina_paired_end,
    sequence_file_set_ultima,
):
    for item in (
        sequence_file_set_illumina_single_end,
        sequence_file_set_illumina_paired_end,
        sequence_file_set_ultima,
    ):
        res = indexer_testapp.get(item['@id'] + '@@index-data')
        assert not any(error['category'] == CATEGORY for error in _audit_errors(res))


def test_sequence_file_set_extra_index_audit(
    testapp,
    indexer_testapp,
    sequence_file_set_illumina_paired_end,
    sequence_file_with_aliases,
):
    testapp.patch_json(
        sequence_file_set_illumina_paired_end['@id'],
        {'index1': sequence_file_with_aliases['@id']},
        status=200,
    )
    res = indexer_testapp.get(sequence_file_set_illumina_paired_end['@id'] + '@@index-data')
    errors = [error for error in _audit_errors(res) if error['category'] == CATEGORY]
    assert len(errors) == 1
    assert errors[0]['level_name'] == 'ERROR'


def test_sequence_file_set_audit_clears_after_fixing_cardinality(
    testapp,
    indexer_testapp,
    sequence_file_set_illumina_paired_end,
    sequence_file_with_aliases,
):
    testapp.patch_json(
        sequence_file_set_illumina_paired_end['@id'],
        {
            'index1': sequence_file_with_aliases['@id'],
            'run_cardinality': 'paired-end-with-index',
        },
        status=200,
    )
    res = indexer_testapp.get(sequence_file_set_illumina_paired_end['@id'] + '@@index-data')
    assert not any(error['category'] == CATEGORY for error in _audit_errors(res))


def test_sequence_file_set_index2_only_with_index_no_audit(
    testapp,
    indexer_testapp,
    sequence_file_set_illumina_paired_end,
    sequence_file_with_aliases,
):
    testapp.patch_json(
        sequence_file_set_illumina_paired_end['@id'],
        {
            'index2': sequence_file_with_aliases['@id'],
            'run_cardinality': 'paired-end-with-index',
        },
        status=200,
    )
    res = indexer_testapp.get(sequence_file_set_illumina_paired_end['@id'] + '@@index-data')
    assert not any(error['category'] == CATEGORY for error in _audit_errors(res))


def _linked_value(**files_by_slot):
    value = {
        '@type': ['SequenceFileSet'],
        '@id': '/sequence-file-sets/b2a1f0d2-0000-4000-8000-000000000001/',
    }
    for slot, file_name in files_by_slot.items():
        value[slot] = f'/sequence-files/{file_name}/'
    return value


@pytest.mark.parametrize('files_by_slot', [
    {},
    {'read1': 'IGVFDTESTA'},
    {'read1': 'IGVFDTESTA', 'read2': 'IGVFDTESTB'},
    {'read1': 'IGVFDTESTA', 'read2': 'IGVFDTESTB', 'read3': 'IGVFDTESTC', 'index1': 'IGVFDTESTD', 'index2': 'IGVFDTESTE'},
    {'untrimmed_cram': 'IGVFDTESTA', 'trimmed_cram': 'IGVFDTESTB'},
])
def test_distinct_sequence_files_no_audit(files_by_slot):
    failures = list(audit_sequence_file_set_duplicate_sequence_file(_linked_value(**files_by_slot), {}))
    assert failures == []


@pytest.mark.parametrize('files_by_slot,expected_slots', [
    ({'read1': 'IGVFDTESTA', 'read2': 'IGVFDTESTA'}, '`read1` and `read2`'),
    ({'untrimmed_cram': 'IGVFDTESTA', 'trimmed_cram': 'IGVFDTESTA'}, '`untrimmed_cram` and `trimmed_cram`'),
    ({'read1': 'IGVFDTESTA', 'trimmed_cram': 'IGVFDTESTA'}, '`read1` and `trimmed_cram`'),
    ({'read2': 'IGVFDTESTB', 'index2': 'IGVFDTESTB', 'read1': 'IGVFDTESTA'}, '`read2` and `index2`'),
])
def test_file_in_two_slots_audit(files_by_slot, expected_slots):
    failures = list(audit_sequence_file_set_duplicate_sequence_file(_linked_value(**files_by_slot), {}))
    assert len(failures) == 1
    assert failures[0].category == DUPLICATE_CATEGORY
    assert failures[0].__json__()['level_name'] == 'ERROR'
    assert f'in {expected_slots}.' in failures[0].detail


def test_file_in_three_slots_one_audit():
    failures = list(audit_sequence_file_set_duplicate_sequence_file(
        _linked_value(read1='IGVFDTESTA', read2='IGVFDTESTA', index1='IGVFDTESTA'), {}))
    assert len(failures) == 1
    assert 'in `read1`, `read2` and `index1`.' in failures[0].detail


def test_two_duplicated_files_two_audits():
    failures = list(audit_sequence_file_set_duplicate_sequence_file(
        _linked_value(read1='IGVFDTESTA', read2='IGVFDTESTA', index1='IGVFDTESTB', index2='IGVFDTESTB'), {}))
    assert len(failures) == 2
    assert 'IGVFDTESTA' in failures[0].detail
    assert 'in `read1` and `read2`.' in failures[0].detail
    assert 'IGVFDTESTB' in failures[1].detail
    assert 'in `index1` and `index2`.' in failures[1].detail


def test_sequence_file_set_fixtures_no_duplicate_audit(
    indexer_testapp,
    sequence_file_set_illumina_single_end,
    sequence_file_set_illumina_paired_end,
    sequence_file_set_ultima,
):
    for item in (
        sequence_file_set_illumina_single_end,
        sequence_file_set_illumina_paired_end,
        sequence_file_set_ultima,
    ):
        res = indexer_testapp.get(item['@id'] + '@@index-data')
        assert not any(error['category'] == DUPLICATE_CATEGORY for error in _audit_errors(res))


def test_sequence_file_set_same_file_in_read1_and_read2_audit(
    testapp,
    indexer_testapp,
    sequence_file_set_illumina_paired_end,
    sequence_file,
):
    testapp.patch_json(
        sequence_file_set_illumina_paired_end['@id'],
        {'read2': sequence_file['@id']},
        status=200,
    )
    res = indexer_testapp.get(sequence_file_set_illumina_paired_end['@id'] + '@@index-data')
    errors = [error for error in _audit_errors(res) if error['category'] == DUPLICATE_CATEGORY]
    assert len(errors) == 1
    assert errors[0]['level_name'] == 'ERROR'
    assert sequence_file['@id'] in errors[0]['detail']


def test_sequence_file_set_same_cram_in_both_slots_audit(
    testapp,
    indexer_testapp,
    sequence_file_set_ultima,
    sequence_file_cram,
):
    testapp.patch_json(
        sequence_file_set_ultima['@id'],
        {'trimmed_cram': sequence_file_cram['@id']},
        status=200,
    )
    res = indexer_testapp.get(sequence_file_set_ultima['@id'] + '@@index-data')
    errors = [error for error in _audit_errors(res) if error['category'] == DUPLICATE_CATEGORY]
    assert len(errors) == 1
    assert errors[0]['level_name'] == 'ERROR'
