import pytest

from igvfd.audit.biosample import (
    audit_biosample_invalid_developmental_stages_ontology,
    audit_biosample_missing_developmental_stages,
)


def _audit_errors(res):
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    return errors_list


def test_biosample_missing_developmental_stages_no_audit():
    value = {
        '@type': ['Tissue'],
        '@id': '/tissues/IGVFDTEST0001/',
        'developmental_stages': ['/controlled-terms/IGVFDTEST0001/'],
    }
    failures = list(audit_biosample_missing_developmental_stages(value, {}))
    assert len(failures) == 0


def test_biosample_missing_developmental_stages_audit():
    value = {
        '@type': ['Tissue'],
        '@id': '/tissues/IGVFDTEST0001/',
    }
    failures = list(audit_biosample_missing_developmental_stages(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'missing developmental stage'


def test_biosample_invalid_developmental_stages_ontology_no_audit():
    value = {
        '@type': ['Tissue'],
        '@id': '/tissues/IGVFDTEST0001/',
        'developmental_stages': [
            {
                '@id': '/controlled-terms/IGVFDTEST0001/',
                'ontology_source': 'HsapDv',
            },
        ],
    }
    failures = list(audit_biosample_invalid_developmental_stages_ontology(value, {}))
    assert len(failures) == 0


def test_biosample_invalid_developmental_stages_ontology_audit():
    value = {
        '@type': ['Tissue'],
        '@id': '/tissues/IGVFDTEST0001/',
        'developmental_stages': [
            {
                '@id': '/controlled-terms/IGVFDTEST0002/',
                'ontology_source': 'UBERON',
            },
        ],
    }
    failures = list(audit_biosample_invalid_developmental_stages_ontology(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'invalid developmental stage'


def test_biosample_invalid_developmental_stages_ontology_zfs_no_audit():
    value = {
        '@type': ['Tissue'],
        '@id': '/tissues/IGVFDTEST0001/',
        'developmental_stages': [
            {
                '@id': '/controlled-terms/IGVFDTEST0003/',
                'ontology_source': 'ZFS',
            },
        ],
    }
    failures = list(audit_biosample_invalid_developmental_stages_ontology(value, {}))
    assert len(failures) == 0


def test_biosample_invalid_developmental_stages_ontology_zfa_audit():
    value = {
        '@type': ['Tissue'],
        '@id': '/tissues/IGVFDTEST0001/',
        'developmental_stages': [
            {
                '@id': '/controlled-terms/IGVFDTEST0004/',
                'ontology_source': 'ZFA',
            },
        ],
    }
    failures = list(audit_biosample_invalid_developmental_stages_ontology(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'invalid developmental stage'


@pytest.mark.parametrize('biosample_type', ['tissue', 'organoid'])
def test_biosample_fixture_missing_developmental_stages_audit(indexer_testapp, biosample_type, request):
    fixture = request.getfixturevalue(biosample_type)
    res = indexer_testapp.get(fixture['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert any(
        error['category'] == 'missing developmental stage'
        for error in errors_list
    )


@pytest.mark.parametrize('biosample_type', ['tissue', 'organoid'])
def test_biosample_with_developmental_stages_missing_audit_clean(
    testapp,
    indexer_testapp,
    other_lab,
    human_donor,
    controlled_term_brain,
    controlled_term_dev_stage_human,
    biosample_type,
):
    config = {
        'tissue': '/tissue',
        'organoid': '/organoid',
    }
    endpoint = config[biosample_type]
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'developmental_stages': [controlled_term_dev_stage_human['@id']],
        'status': 'current',
    }
    biosample = testapp.post_json(endpoint, item, status=201).json['@graph'][0]
    res = indexer_testapp.get(biosample['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert not any(
        error['category'] == 'missing developmental stage'
        for error in errors_list
    )


@pytest.mark.parametrize('biosample_type', ['tissue', 'organoid'])
def test_biosample_invalid_developmental_stages_ontology_integration(
    testapp,
    indexer_testapp,
    other_lab,
    human_donor,
    controlled_term_brain,
    biosample_type,
):
    config = {
        'tissue': '/tissue',
        'organoid': '/organoid',
    }
    endpoint = config[biosample_type]
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'developmental_stages': [controlled_term_brain['@id']],
        'status': 'current',
    }
    biosample = testapp.post_json(endpoint, item, status=201).json['@graph'][0]
    res = indexer_testapp.get(biosample['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert any(
        error['category'] == 'invalid developmental stage'
        for error in errors_list
    )


def test_tissue_with_developmental_stages_fixture_missing_audit_clean(
    indexer_testapp,
    tissue_with_developmental_stages,
):
    res = indexer_testapp.get(tissue_with_developmental_stages['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert not any(
        error['category'] == 'missing developmental stage'
        for error in errors_list
    )


@pytest.mark.parametrize('biosample_type', ['tissue', 'organoid'])
def test_biosample_with_zebrafish_developmental_stages_audit_clean(
    testapp,
    indexer_testapp,
    other_lab,
    human_donor,
    controlled_term_brain,
    controlled_term_dev_stage_zebrafish,
    biosample_type,
):
    config = {
        'tissue': '/tissue',
        'organoid': '/organoid',
    }
    endpoint = config[biosample_type]
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'developmental_stages': [controlled_term_dev_stage_zebrafish['@id']],
        'status': 'current',
    }
    biosample = testapp.post_json(endpoint, item, status=201).json['@graph'][0]
    res = indexer_testapp.get(biosample['@id'] + '@@index-data')
    errors_list = _audit_errors(res)
    assert not any(
        error['category'] == 'missing developmental stage'
        for error in errors_list
    )
    assert not any(
        error['category'] == 'invalid developmental stage'
        for error in errors_list
    )
