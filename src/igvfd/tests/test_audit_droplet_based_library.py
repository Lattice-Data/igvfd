from igvfd.audit.library import (
    audit_dual_cardinality_self_linked_library,
    audit_library_samples_missing_multiplexing_barcodes,
    audit_library_samples_unexpected_multiplexing_barcodes,
    audit_single_cardinality_unexpected_linked_libraries,
)


def _audit_errors(res):
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    return errors_list


def test_single_cardinality_unexpected_linked_libraries():
    value = {
        '@type': ['DropletBasedLibrary'],
        '@id': '/droplet-based-libraries/IGVFDTEST0001/',
        'library_cardinality': 'single',
        'linked_libraries': ['/droplet-based-libraries/IGVFDTEST0002/'],
    }
    failures = list(audit_single_cardinality_unexpected_linked_libraries(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'unexpected linked libraries'


def test_single_cardinality_no_linked_libraries_no_audit():
    value = {
        '@type': ['DropletBasedLibrary'],
        '@id': '/droplet-based-libraries/IGVFDTEST0001/',
        'library_cardinality': 'single',
    }
    failures = list(audit_single_cardinality_unexpected_linked_libraries(value, {}))
    assert len(failures) == 0


def test_dual_cardinality_self_linked_library_audit():
    value = {
        '@type': ['DropletBasedLibrary'],
        '@id': '/droplet-based-libraries/IGVFDTEST0001/',
        'library_cardinality': 'dual',
        'linked_libraries': ['/droplet-based-libraries/IGVFDTEST0001/'],
    }
    failures = list(audit_dual_cardinality_self_linked_library(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'self linked library'


def test_dual_cardinality_self_linked_library_via_uuid_audit():
    value = {
        '@type': ['DropletBasedLibrary'],
        '@id': '/droplet-based-libraries/IGVFDTEST0001/',
        'uuid': 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        'library_cardinality': 'dual',
        'linked_libraries': ['a1b2c3d4-e5f6-7890-abcd-ef1234567890'],
    }
    failures = list(audit_dual_cardinality_self_linked_library(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'self linked library'


def test_dual_cardinality_self_linked_library_via_alias_audit():
    value = {
        '@type': ['DropletBasedLibrary'],
        '@id': '/droplet-based-libraries/IGVFDTEST0001/',
        'aliases': ['lattice:droplet-partner-a'],
        'library_cardinality': 'dual',
        'linked_libraries': ['lattice:droplet-partner-a'],
    }
    failures = list(audit_dual_cardinality_self_linked_library(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'self linked library'


def test_dual_cardinality_other_linked_library_no_self_audit():
    value = {
        '@type': ['DropletBasedLibrary'],
        '@id': '/droplet-based-libraries/IGVFDTEST0001/',
        'library_cardinality': 'dual',
        'linked_libraries': ['/droplet-based-libraries/IGVFDTEST0002/'],
    }
    failures = list(audit_dual_cardinality_self_linked_library(value, {}))
    assert len(failures) == 0


def test_droplet_based_library_samples_without_multiplexing_barcodes_no_audit():
    value = {
        '@type': ['DropletBasedLibrary'],
        '@id': '/droplet-based-libraries/IGVFDTEST0001/',
        'library_cardinality': 'single',
        'samples': [
            {
                '@id': '/tissues/IGVFDTEST0001/',
            },
        ],
    }
    failures = list(audit_library_samples_unexpected_multiplexing_barcodes(value, {}))
    assert len(failures) == 0


def test_droplet_based_library_sample_with_multiplexing_barcodes_audit():
    value = {
        '@type': ['DropletBasedLibrary'],
        '@id': '/droplet-based-libraries/IGVFDTEST0001/',
        'library_cardinality': 'single',
        'samples': [
            {
                '@id': '/tissues/IGVFDTEST0001/',
                'multiplexing_barcodes': ['P01-A1'],
            },
        ],
    }
    failures = list(audit_library_samples_unexpected_multiplexing_barcodes(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'unexpected multiplexing barcodes'


def test_droplet_based_library_with_multiplexing_method_all_samples_have_barcodes_no_audit():
    value = {
        '@type': ['DropletBasedLibrary'],
        '@id': '/droplet-based-libraries/IGVFDTEST0001/',
        'library_cardinality': 'single',
        'multiplexing_method': ['antibody hashing'],
        'samples': [
            {
                '@id': '/tissues/IGVFDTEST0001/',
                'multiplexing_barcodes': ['A0251'],
            },
            {
                '@id': '/tissues/IGVFDTEST0002/',
                'multiplexing_barcodes': ['A0252'],
            },
        ],
    }
    missing_failures = list(audit_library_samples_missing_multiplexing_barcodes(value, {}))
    unexpected_failures = list(audit_library_samples_unexpected_multiplexing_barcodes(value, {}))
    assert len(missing_failures) == 0
    assert len(unexpected_failures) == 0


def test_droplet_based_library_with_multiplexing_method_missing_barcodes_audit():
    value = {
        '@type': ['DropletBasedLibrary'],
        '@id': '/droplet-based-libraries/IGVFDTEST0001/',
        'library_cardinality': 'single',
        'multiplexing_method': ['antibody hashing'],
        'samples': [
            {
                '@id': '/tissues/IGVFDTEST0001/',
                'multiplexing_barcodes': ['A0251'],
            },
            {
                '@id': '/tissues/IGVFDTEST0002/',
            },
        ],
    }
    failures = list(audit_library_samples_missing_multiplexing_barcodes(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'missing multiplexing barcodes'


def test_droplet_based_library_with_multiplexing_method_no_unexpected_audit():
    value = {
        '@type': ['DropletBasedLibrary'],
        '@id': '/droplet-based-libraries/IGVFDTEST0001/',
        'library_cardinality': 'single',
        'multiplexing_method': ['antibody hashing'],
        'samples': [
            {
                '@id': '/tissues/IGVFDTEST0001/',
                'multiplexing_barcodes': ['BC001'],
            },
            {
                '@id': '/tissues/IGVFDTEST0002/',
                'multiplexing_barcodes': ['BC016'],
            },
        ],
    }
    failures = list(audit_library_samples_unexpected_multiplexing_barcodes(value, {}))
    assert len(failures) == 0


def test_single_cardinality_fixture_clean(indexer_testapp, droplet_based_library):
    res = indexer_testapp.get(droplet_based_library['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert not any(
        error['category'] == 'unexpected linked libraries'
        for error in errors_list
    )
    assert not any(
        error['category'] == 'unexpected multiplexing barcodes'
        for error in errors_list
    )


def test_droplet_based_library_fixture_unexpected_multiplexing_barcodes(
    testapp,
    indexer_testapp,
    droplet_based_library,
):
    tissue_id = droplet_based_library['samples'][0]
    testapp.patch_json(tissue_id, {'multiplexing_barcodes': ['P01-A1']}, status=200)
    res = indexer_testapp.get(droplet_based_library['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert any(
        error['category'] == 'unexpected multiplexing barcodes'
        for error in errors_list
    )


def test_droplet_based_library_fixture_multiplexed_clean(
    testapp,
    indexer_testapp,
    other_lab,
    human_donor,
    controlled_term_brain,
):
    tissue_base = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'status': 'current',
    }
    tissue_one = testapp.post_json(
        '/tissue',
        {**tissue_base, 'multiplexing_barcodes': ['BC001']},
        status=201,
    ).json['@graph'][0]
    tissue_two = testapp.post_json(
        '/tissue',
        {**tissue_base, 'multiplexing_barcodes': ['BC016'], 'aliases': ['lattice:pytest-droplet-barcode-2']},
        status=201,
    ).json['@graph'][0]
    library_item = {
        'lab': other_lab['@id'],
        'samples': [tissue_one['@id'], tissue_two['@id']],
        'multiplexing_method': ['antibody hashing'],
        'library_cardinality': 'single',
        'status': 'current',
    }
    library = testapp.post_json('/droplet_based_library', library_item, status=201).json['@graph'][0]
    res = indexer_testapp.get(library['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert not any(
        error['category'] == 'missing multiplexing barcodes'
        for error in errors_list
    )
    assert not any(
        error['category'] == 'unexpected multiplexing barcodes'
        for error in errors_list
    )


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
    droplet_based_library_with_feature_types,
):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'dual',
        'linked_libraries': [
            droplet_based_library['@id'],
            droplet_based_library_with_feature_types['@id'],
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
    indexer_testapp,
    droplet_based_library_dual_with_linked_library,
):
    dual_library = droplet_based_library_dual_with_linked_library
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
    assert not any(
        error['category'] == 'unexpected linked libraries'
        for error in errors_list
    )
    assert not any(
        error['category'] == 'self linked library'
        for error in errors_list
    )


def test_dual_cardinality_self_linked_library(
    testapp,
    indexer_testapp,
    droplet_based_library_dual,
):
    dual_library = droplet_based_library_dual
    testapp.patch_json(
        dual_library['@id'],
        {'linked_libraries': [dual_library['@id']]},
        status=200,
    )
    res = indexer_testapp.get(dual_library['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert any(
        error['category'] == 'self linked library'
        for error in errors_list
    )
