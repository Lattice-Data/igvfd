from igvfd.audit.treatment import audit_treatment_non_chebi_uniprot_ontological_term


def _audit_errors(res):
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    return errors_list


def test_chebi_term_no_audit():
    value = {
        '@type': ['Treatment'],
        '@id': '/treatments/IGVFDTEST0001/',
        'ontological_term': {
            '@id': '/controlled-terms/CHEBI:15377/',
            'ontology_source': 'CHEBI',
        },
    }
    assert list(audit_treatment_non_chebi_uniprot_ontological_term(value, {})) == []


def test_uniprot_term_no_audit():
    value = {
        '@type': ['Treatment'],
        '@id': '/treatments/IGVFDTEST0001/',
        'ontological_term': {
            '@id': '/controlled-terms/uniprot:P01308/',
            'ontology_source': 'UniProt',
        },
    }
    assert list(audit_treatment_non_chebi_uniprot_ontological_term(value, {})) == []


def test_cl_term_fires_error():
    value = {
        '@type': ['Treatment'],
        '@id': '/treatments/IGVFDTEST0001/',
        'ontological_term': {
            '@id': '/controlled-terms/CL:0000005/',
            'ontology_source': 'CL',
        },
    }
    failures = list(audit_treatment_non_chebi_uniprot_ontological_term(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'invalid ontological term'


def test_missing_ontological_term_no_audit():
    value = {
        '@type': ['Treatment'],
        '@id': '/treatments/IGVFDTEST0001/',
    }
    assert list(audit_treatment_non_chebi_uniprot_ontological_term(value, {})) == []


def test_treatment_chebi_term_clean(indexer_testapp, treatment):
    res = indexer_testapp.get(treatment['@id'] + '@@index-data')
    assert not any(
        error['category'] == 'invalid ontological term'
        for error in _audit_errors(res)
    )


def test_treatment_cl_term_fires_audit(testapp, indexer_testapp, other_lab, controlled_term):
    item = {
        'lab': other_lab['@id'],
        'ontological_term': controlled_term['@id'],
        'status': 'current',
    }
    treatment = testapp.post_json('/treatment', item, status=201).json['@graph'][0]
    res = indexer_testapp.get(treatment['@id'] + '@@index-data')
    assert any(
        error['category'] == 'invalid ontological term'
        for error in _audit_errors(res)
    )


def test_treatment_uniprot_term_clean(
    testapp,
    indexer_testapp,
    other_lab,
    controlled_term_uniprot,
):
    item = {
        'lab': other_lab['@id'],
        'ontological_term': controlled_term_uniprot['@id'],
        'status': 'current',
    }
    treatment = testapp.post_json('/treatment', item, status=201).json['@graph'][0]
    res = indexer_testapp.get(treatment['@id'] + '@@index-data')
    assert not any(
        error['category'] == 'invalid ontological term'
        for error in _audit_errors(res)
    )
