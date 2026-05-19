def _audit_errors(res):
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    return errors_list


def test_dual_cardinality_missing_linked_libraries(testapp, indexer_testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'dual',
        'status': 'current',
    }
    dual_library = testapp.post_json('/droplet_based_library', item, status=201).json['@graph'][0]
    res = indexer_testapp.get(dual_library['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert any(
        error['category'] == 'missing linked libraries'
        for error in errors_list
    )


def test_dual_cardinality_multiple_linked_libraries(
    testapp,
    indexer_testapp,
    other_lab,
    tissue,
    droplet_based_library,
    droplet_based_library_with_chemistry_version,
):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'dual',
        'linked_libraries': [
            droplet_based_library['@id'],
            droplet_based_library_with_chemistry_version['@id'],
        ],
        'status': 'current',
    }
    dual_library = testapp.post_json('/droplet_based_library', item, status=201).json['@graph'][0]
    res = indexer_testapp.get(dual_library['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert any(
        error['category'] == 'unexpected number of linked libraries'
        for error in errors_list
    )


def test_dual_cardinality_exactly_one_linked_library(
    testapp,
    indexer_testapp,
    other_lab,
    tissue,
    droplet_based_library,
):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'dual',
        'linked_libraries': [droplet_based_library['@id']],
        'status': 'current',
    }
    dual_library = testapp.post_json('/droplet_based_library', item, status=201).json['@graph'][0]
    res = indexer_testapp.get(dual_library['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert not any(
        error['category'] == 'missing linked libraries'
        for error in errors_list
    )
    assert not any(
        error['category'] == 'unexpected number of linked libraries'
        for error in errors_list
    )
