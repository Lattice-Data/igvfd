from igvfd.audit.library import (
    audit_plate_based_library_samples_missing_hash_index,
)


def _audit_errors(res):
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    return errors_list


def test_plate_based_library_all_samples_have_hash_index_no_audit():
    value = {
        '@type': ['PlateBasedLibrary'],
        '@id': '/plate-based-libraries/IGVFDTEST0001/',
        'samples': [
            {
                '@id': '/tissues/IGVFDTEST0001/',
                'hash_index': 'P01-A1',
            },
            {
                '@id': '/tissues/IGVFDTEST0002/',
                'hash_index': 'P01-A2',
            },
        ],
    }
    failures = list(audit_plate_based_library_samples_missing_hash_index(value, {}))
    assert len(failures) == 0


def test_plate_based_library_sample_missing_hash_index_audit():
    value = {
        '@type': ['PlateBasedLibrary'],
        '@id': '/plate-based-libraries/IGVFDTEST0001/',
        'samples': [
            {
                '@id': '/tissues/IGVFDTEST0001/',
                'hash_index': 'P01-A1',
            },
            {
                '@id': '/tissues/IGVFDTEST0002/',
            },
        ],
    }
    failures = list(audit_plate_based_library_samples_missing_hash_index(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'missing hash index'


def test_plate_based_library_fixture_missing_hash_index(
    indexer_testapp,
    plate_based_library,
):
    res = indexer_testapp.get(plate_based_library['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert any(
        error['category'] == 'missing hash index'
        for error in errors_list
    )


def test_plate_based_library_fixture_with_hash_index_clean(
    testapp,
    indexer_testapp,
    other_lab,
    human_donor,
    controlled_term_brain,
):
    tissue_item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'hash_index': 'P01-A1',
        'status': 'current',
    }
    tissue = testapp.post_json('/tissue', tissue_item, status=201).json['@graph'][0]
    library_item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'status': 'current',
    }
    library = testapp.post_json('/plate_based_library', library_item, status=201).json['@graph'][0]
    res = indexer_testapp.get(library['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert not any(
        error['category'] == 'missing hash index'
        for error in errors_list
    )
