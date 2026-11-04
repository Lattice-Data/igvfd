def _linked_to_deleted_errors(res):
    errors = res.json['audit']
    return [
        error
        for errors_by_level in errors.values()
        for error in errors_by_level
        if error['category'] == 'linked to deleted object'
    ]


def test_item_linked_to_current_objects_no_audit(indexer_testapp, tissue):
    res = indexer_testapp.get(tissue['@id'] + '@@index-data')
    assert _linked_to_deleted_errors(res) == []


def test_item_linked_to_deleted_object_in_array_audit(testapp, indexer_testapp, tissue, controlled_term_brain):
    testapp.patch_json(controlled_term_brain['@id'], {'status': 'deleted'})
    res = indexer_testapp.get(tissue['@id'] + '@@index-data')
    errors = _linked_to_deleted_errors(res)
    assert len(errors) == 1
    assert errors[0]['level_name'] == 'ERROR'
    assert '`sample_terms`' in errors[0]['detail']
    assert controlled_term_brain['@id'] in errors[0]['detail']


def test_item_linked_to_deleted_object_single_link_audit(testapp, indexer_testapp, human_donor, taxon_homo_sapiens):
    testapp.patch_json(taxon_homo_sapiens['@id'], {'status': 'deleted'})
    res = indexer_testapp.get(human_donor['@id'] + '@@index-data')
    errors = _linked_to_deleted_errors(res)
    assert len(errors) == 1
    assert '`taxa`' in errors[0]['detail']


def test_item_linked_to_deleted_objects_one_audit_per_property(
    testapp,
    indexer_testapp,
    tissue,
    human_donor,
    controlled_term_brain,
):
    testapp.patch_json(controlled_term_brain['@id'], {'status': 'deleted'})
    testapp.patch_json(human_donor['@id'], {'status': 'deleted'})
    res = indexer_testapp.get(tissue['@id'] + '@@index-data')
    details = sorted(error['detail'] for error in _linked_to_deleted_errors(res))
    assert len(details) == 2
    assert '`donors`' in details[0]
    assert '`sample_terms`' in details[1]


def test_item_submitted_by_deleted_user_no_audit(testapp, indexer_testapp, submitter, other_lab, taxon_homo_sapiens):
    item = {
        'lab': other_lab['@id'],
        'taxa': taxon_homo_sapiens['@id'],
        'sex': 'unspecified',
        'cxg_donor_id': 'lattice:test-cxg-submitted-by-deleted-user',
        'submitted_by': submitter['@id'],
    }
    human_donor = testapp.post_json('/human_donor', item, status=201).json['@graph'][0]
    testapp.patch_json(submitter['@id'], {'status': 'deleted'})
    res = indexer_testapp.get(human_donor['@id'] + '@@index-data')
    assert res.json['object']['submitted_by'] == submitter['@id']
    assert _linked_to_deleted_errors(res) == []


def test_deleted_item_linked_to_deleted_object_no_audit(testapp, indexer_testapp, tissue, controlled_term_brain):
    testapp.patch_json(controlled_term_brain['@id'], {'status': 'deleted'})
    testapp.patch_json(tissue['@id'], {'status': 'deleted'})
    res = indexer_testapp.get(tissue['@id'] + '@@index-data')
    assert _linked_to_deleted_errors(res) == []
