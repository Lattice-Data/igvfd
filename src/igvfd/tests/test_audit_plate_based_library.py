from igvfd.audit.library import (
    audit_library_samples_missing_multiplexing_barcodes,
    audit_library_samples_unexpected_multiplexing_barcodes,
    audit_plate_based_library_samples_missing_rt_indexes,
)


def _audit_errors(res):
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    return errors_list


def test_plate_based_library_all_samples_have_multiplexing_barcodes_no_audit():
    value = {
        '@type': ['PlateBasedLibrary'],
        '@id': '/plate-based-libraries/IGVFDTEST0001/',
        'multiplexing_method': ['combinatorial indexing'],
        'samples': [
            {
                '@id': '/tissues/IGVFDTEST0001/',
                'multiplexing_barcodes': ['P01-A1'],
            },
            {
                '@id': '/tissues/IGVFDTEST0002/',
                'multiplexing_barcodes': ['P01-A2'],
            },
        ],
    }
    failures = list(audit_library_samples_missing_multiplexing_barcodes(value, {}))
    assert len(failures) == 0


def test_plate_based_library_sample_missing_multiplexing_barcodes_audit():
    value = {
        '@type': ['PlateBasedLibrary'],
        '@id': '/plate-based-libraries/IGVFDTEST0001/',
        'multiplexing_method': ['combinatorial indexing'],
        'samples': [
            {
                '@id': '/tissues/IGVFDTEST0001/',
                'multiplexing_barcodes': ['P01-A1'],
            },
            {
                '@id': '/tissues/IGVFDTEST0002/',
            },
        ],
    }
    failures = list(audit_library_samples_missing_multiplexing_barcodes(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'missing multiplexing barcodes'


def test_plate_based_library_ngv_all_samples_without_barcodes_no_audit():
    value = {
        '@type': ['PlateBasedLibrary'],
        '@id': '/plate-based-libraries/IGVFDTEST0001/',
        'multiplexing_method': ['natural genetic variation'],
        'samples': [
            {
                '@id': '/tissues/IGVFDTEST0001/',
            },
            {
                '@id': '/tissues/IGVFDTEST0002/',
            },
        ],
    }
    missing_failures = list(audit_library_samples_missing_multiplexing_barcodes(value, {}))
    unexpected_failures = list(audit_library_samples_unexpected_multiplexing_barcodes(value, {}))
    assert len(missing_failures) == 0
    assert len(unexpected_failures) == 0


def test_plate_based_library_ngv_sample_with_barcodes_unexpected_audit():
    value = {
        '@type': ['PlateBasedLibrary'],
        '@id': '/plate-based-libraries/IGVFDTEST0001/',
        'multiplexing_method': ['natural genetic variation'],
        'samples': [
            {
                '@id': '/tissues/IGVFDTEST0001/',
            },
            {
                '@id': '/tissues/IGVFDTEST0002/',
                'multiplexing_barcodes': ['P01-A1'],
            },
        ],
    }
    missing_failures = list(audit_library_samples_missing_multiplexing_barcodes(value, {}))
    unexpected_failures = list(audit_library_samples_unexpected_multiplexing_barcodes(value, {}))
    assert len(missing_failures) == 0
    assert len(unexpected_failures) == 1
    assert unexpected_failures[0].category == 'unexpected multiplexing barcodes'


def test_plate_based_library_ngv_missing_barcodes_no_missing_audit():
    value = {
        '@type': ['PlateBasedLibrary'],
        '@id': '/plate-based-libraries/IGVFDTEST0001/',
        'multiplexing_method': ['natural genetic variation'],
        'samples': [
            {
                '@id': '/tissues/IGVFDTEST0001/',
            },
            {
                '@id': '/tissues/IGVFDTEST0002/',
            },
        ],
    }
    failures = list(audit_library_samples_missing_multiplexing_barcodes(value, {}))
    assert len(failures) == 0


def test_plate_based_library_without_multiplexing_method_no_barcode_audit():
    value = {
        '@type': ['PlateBasedLibrary'],
        '@id': '/plate-based-libraries/IGVFDTEST0001/',
        'samples': [
            {
                '@id': '/tissues/IGVFDTEST0001/',
            },
        ],
    }
    missing_failures = list(audit_library_samples_missing_multiplexing_barcodes(value, {}))
    unexpected_failures = list(audit_library_samples_unexpected_multiplexing_barcodes(value, {}))
    assert len(missing_failures) == 0
    assert len(unexpected_failures) == 0


def test_plate_based_library_without_multiplexing_method_unexpected_barcodes_audit():
    value = {
        '@type': ['PlateBasedLibrary'],
        '@id': '/plate-based-libraries/IGVFDTEST0001/',
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


def test_plate_based_library_fixture_no_missing_multiplexing_barcodes_audit(
    indexer_testapp,
    plate_based_library,
):
    res = indexer_testapp.get(plate_based_library['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert not any(
        error['category'] == 'missing multiplexing barcodes'
        for error in errors_list
    )


def test_plate_based_library_fixture_unexpected_multiplexing_barcodes(
    testapp,
    indexer_testapp,
    plate_based_library,
):
    tissue_id = plate_based_library['samples'][0]
    testapp.patch_json(tissue_id, {'multiplexing_barcodes': ['P01-A1']}, status=200)
    res = indexer_testapp.get(plate_based_library['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert any(
        error['category'] == 'unexpected multiplexing barcodes'
        for error in errors_list
    )


def test_plate_based_library_fixture_with_multiplexing_method_missing_barcodes(
    testapp,
    indexer_testapp,
    other_lab,
    tissue,
    tissue_with_aliases,
):
    library_item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id'], tissue_with_aliases['@id']],
        'multiplexing_method': ['combinatorial indexing'],
        'status': 'current',
    }
    library = testapp.post_json('/plate_based_library', library_item, status=201).json['@graph'][0]
    res = indexer_testapp.get(library['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert any(
        error['category'] == 'missing multiplexing barcodes'
        for error in errors_list
    )


def test_plate_based_library_fixture_with_multiplexing_barcodes_clean(
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
        {**tissue_base, 'multiplexing_barcodes': ['P01-A1']},
        status=201,
    ).json['@graph'][0]
    tissue_two = testapp.post_json(
        '/tissue',
        {**tissue_base, 'multiplexing_barcodes': ['P01-A2'], 'aliases': ['lattice:pytest-tissue-barcode-2']},
        status=201,
    ).json['@graph'][0]
    library_item = {
        'lab': other_lab['@id'],
        'samples': [tissue_one['@id'], tissue_two['@id']],
        'multiplexing_method': ['antibody hashing'],
        'status': 'current',
    }
    library = testapp.post_json('/plate_based_library', library_item, status=201).json['@graph'][0]
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


def test_plate_based_library_all_samples_have_rt_indexes_no_audit():
    value = {
        '@type': ['PlateBasedLibrary'],
        '@id': '/plate-based-libraries/IGVFDTEST0001/',
        'samples': [
            {
                '@id': '/tissues/IGVFDTEST0001/',
                'RT_indexes': ['SCALEQUANT-A1'],
            },
            {
                '@id': '/tissues/IGVFDTEST0002/',
                'RT_indexes': ['SCALEQUANT-A2'],
            },
        ],
    }
    failures = list(audit_plate_based_library_samples_missing_rt_indexes(value, {}))
    assert len(failures) == 0


def test_plate_based_library_sample_missing_rt_indexes_audit():
    value = {
        '@type': ['PlateBasedLibrary'],
        '@id': '/plate-based-libraries/IGVFDTEST0001/',
        'samples': [
            {
                '@id': '/tissues/IGVFDTEST0001/',
                'RT_indexes': ['SCALEQUANT-A1'],
            },
            {
                '@id': '/tissues/IGVFDTEST0002/',
            },
        ],
    }
    failures = list(audit_plate_based_library_samples_missing_rt_indexes(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'missing RT indexes'


def test_plate_based_library_fixture_missing_rt_indexes(
    testapp,
    indexer_testapp,
    plate_based_library,
):
    res = indexer_testapp.get(plate_based_library['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert any(
        error['category'] == 'missing RT indexes'
        for error in errors_list
    )


def test_plate_based_library_fixture_with_rt_indexes_clean(
    testapp,
    indexer_testapp,
    plate_based_library,
):
    tissue_id = plate_based_library['samples'][0]
    testapp.patch_json(
        tissue_id,
        {'RT_indexes': ['SCALEQUANT-A1', 'SCALEQUANT-A2']},
        status=200,
    )
    res = indexer_testapp.get(plate_based_library['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert not any(
        error['category'] == 'missing RT indexes'
        for error in errors_list
    )
