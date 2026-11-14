CATEGORY = 'multiple sequence file sets'


def _errors(indexer_testapp, item):
    res = indexer_testapp.get(item['@id'] + '@@index-data')
    errors = res.json['audit']
    return [
        error
        for level in errors
        for error in errors[level]
        if error['category'] == CATEGORY
    ]


def test_sequence_file_in_one_set_no_audit(
    indexer_testapp,
    sequence_file,
    sequence_file_with_description,
    sequence_file_set_illumina_paired_end,
):
    assert _errors(indexer_testapp, sequence_file) == []
    assert _errors(indexer_testapp, sequence_file_with_description) == []


def test_sequence_file_in_two_sets_audit(
    indexer_testapp,
    sequence_file,
    sequence_file_with_description,
    sequence_file_set_illumina_single_end,
    sequence_file_set_illumina_paired_end,
):
    # both fixtures put sequence_file in read1
    [error] = _errors(indexer_testapp, sequence_file)
    assert error['level_name'] == 'ERROR'
    assert sequence_file['@id'] in error['detail']
    assert sequence_file_set_illumina_single_end['@id'] in error['detail']
    assert sequence_file_set_illumina_paired_end['@id'] in error['detail']
    # read2 of the paired-end set is in no other set
    assert _errors(indexer_testapp, sequence_file_with_description) == []


def test_sequence_file_audit_clears_after_deleting_a_set(
    testapp,
    indexer_testapp,
    sequence_file,
    sequence_file_set_illumina_single_end,
    sequence_file_set_illumina_paired_end,
):
    testapp.patch_json(
        sequence_file_set_illumina_single_end['@id'],
        {'status': 'deleted'},
        status=200,
    )
    assert _errors(indexer_testapp, sequence_file) == []


def test_sequence_file_audit_names_only_non_deleted_sets(
    testapp,
    indexer_testapp,
    other_lab,
    sequence_file,
    droplet_based_library,
    sequence_file_set_illumina_single_end,
    sequence_file_set_illumina_paired_end,
):
    third = testapp.post_json('/sequence_file_set', {
        'lab': other_lab['@id'],
        'library': droplet_based_library['@id'],
        'run_cardinality': 'single-end',
        'read1': sequence_file['@id'],
        'status': 'current',
    }, status=201).json['@graph'][0]
    testapp.patch_json(
        sequence_file_set_illumina_single_end['@id'],
        {'status': 'deleted'},
        status=200,
    )
    [error] = _errors(indexer_testapp, sequence_file)
    assert sequence_file_set_illumina_paired_end['@id'] in error['detail']
    assert third['@id'] in error['detail']
    assert sequence_file_set_illumina_single_end['@id'] not in error['detail']


def test_sequence_file_in_two_slots_of_one_set_no_audit(
    testapp,
    indexer_testapp,
    sequence_file,
    sequence_file_set_illumina_paired_end,
):
    # one set, two slots: two reverse links but one set (the DB2-88 case)
    testapp.patch_json(
        sequence_file_set_illumina_paired_end['@id'],
        {'index1': sequence_file['@id'], 'run_cardinality': 'paired-end-with-index'},
        status=200,
    )
    res = testapp.get(sequence_file['@id'])
    assert res.json['sequence_file_sets'] == [sequence_file_set_illumina_paired_end['@id']]
    assert _errors(indexer_testapp, sequence_file) == []
