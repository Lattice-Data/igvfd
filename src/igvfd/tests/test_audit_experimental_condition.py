import pytest

from igvfd.audit.experimental_condition import audit_experimental_condition_controlled_term_ontology_source


def _audit_errors(res):
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    return errors_list


def _value(*ontology_sources):
    return {
        '@type': ['ExperimentalCondition'],
        '@id': '/experimental_conditions/IGVFDTEST0001/',
        'controlled_terms': [
            {'@id': f'/controlled-terms/TEST:000000{index}/', 'ontology_source': source}
            for index, source in enumerate(ontology_sources)
        ],
    }


@pytest.mark.parametrize('ontology_sources', [('CHEBI',), ('UniProt',), ('EFO',), ('CHEBI', 'UniProt', 'EFO')])
def test_expected_ontology_sources_no_audit(ontology_sources):
    value = _value(*ontology_sources)
    assert list(audit_experimental_condition_controlled_term_ontology_source(value, {})) == []


@pytest.mark.parametrize('ontology_source', ['CL', 'MONDO', 'UBERON'])
def test_unexpected_ontology_source_fires_warning(ontology_source):
    value = _value('UniProt', ontology_source)
    failures = list(audit_experimental_condition_controlled_term_ontology_source(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'invalid ontological term'
    assert failures[0].__json__()['level_name'] == 'WARNING'
    assert '/controlled-terms/TEST:0000001/' in failures[0].detail
    assert f'`{ontology_source}`, expected CHEBI, UniProt or EFO.' in failures[0].detail


def test_one_warning_per_unexpected_term():
    value = _value('CL', 'EFO', 'MONDO')
    failures = list(audit_experimental_condition_controlled_term_ontology_source(value, {}))
    assert len(failures) == 2


def test_description_only_condition_no_audit():
    value = {
        '@type': ['ExperimentalCondition'],
        '@id': '/experimental_conditions/IGVFDTEST0001/',
        'description': 'Cold storage condition',
    }
    assert list(audit_experimental_condition_controlled_term_ontology_source(value, {})) == []


def test_uniprot_term_clean(indexer_testapp, experimental_condition_single_term):
    res = indexer_testapp.get(experimental_condition_single_term['@id'] + '@@index-data')
    assert not any(
        error['category'] == 'invalid ontological term'
        for error in _audit_errors(res)
    )


def test_cl_term_fires_warning(testapp, indexer_testapp, other_lab, controlled_term):
    item = {
        'lab': other_lab['@id'],
        'controlled_terms': [controlled_term['@id']],
        'status': 'current',
    }
    condition = testapp.post_json('/experimental_condition', item, status=201).json['@graph'][0]
    res = indexer_testapp.get(condition['@id'] + '@@index-data')
    assert any(
        error['category'] == 'invalid ontological term'
        for error in res.json['audit'].get('WARNING', [])
    )
