import pytest

from igvfd.audit.experimental_condition import audit_experimental_condition_treatment_ontology_source


def _audit_errors(res):
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    return errors_list


def _value(condition, ontology_source=None):
    value = {
        '@type': ['ExperimentalCondition'],
        '@id': '/experimental_conditions/IGVFDTEST0001/',
        'condition': condition,
    }
    if ontology_source is not None:
        value['controlled_term'] = {
            '@id': '/controlled-terms/TEST:0000001/',
            'ontology_source': ontology_source,
        }
    return value


@pytest.mark.parametrize(
    'condition,ontology_source',
    [
        ('chemical treatment', 'CHEBI'),
        ('protein treatment', 'UniProt'),
        ('diet', 'EFO'),
    ]
)
def test_expected_ontology_source_no_audit(condition, ontology_source):
    value = _value(condition, ontology_source)
    assert list(audit_experimental_condition_treatment_ontology_source(value, {})) == []


@pytest.mark.parametrize(
    'condition,ontology_source',
    [
        ('chemical treatment', 'UniProt'),
        ('chemical treatment', 'CL'),
        ('protein treatment', 'CHEBI'),
    ]
)
def test_unexpected_ontology_source_fires_error(condition, ontology_source):
    value = _value(condition, ontology_source)
    failures = list(audit_experimental_condition_treatment_ontology_source(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'invalid ontological term'


def test_treatment_without_controlled_term_no_audit():
    value = _value('chemical treatment')
    assert list(audit_experimental_condition_treatment_ontology_source(value, {})) == []


def test_protein_treatment_uniprot_term_clean(indexer_testapp, experimental_condition_protein_treatment):
    res = indexer_testapp.get(experimental_condition_protein_treatment['@id'] + '@@index-data')
    assert not any(
        error['category'] == 'invalid ontological term'
        for error in _audit_errors(res)
    )


def test_chemical_treatment_cl_term_fires_audit(testapp, indexer_testapp, other_lab, controlled_term):
    item = {
        'lab': other_lab['@id'],
        'condition': 'chemical treatment',
        'controlled_term': controlled_term['@id'],
        'status': 'current',
    }
    condition = testapp.post_json('/experimental_condition', item, status=201).json['@graph'][0]
    res = indexer_testapp.get(condition['@id'] + '@@index-data')
    assert any(
        error['category'] == 'invalid ontological term'
        for error in _audit_errors(res)
    )
