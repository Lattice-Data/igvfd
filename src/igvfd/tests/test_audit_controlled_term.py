import pytest

from igvfd.audit.controlled_term import audit_controlled_term_deprecated


CATEGORY = 'deprecated ontological term'


def _audit_errors(res):
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    return errors_list


def _system(ontology):
    return {'registry': {'ontology': ontology}}


def _value(term_id):
    return {
        '@type': ['ControlledTerm', 'Item'],
        '@id': f'/controlled-terms/{term_id}/',
        'term_id': term_id,
    }


def test_deprecated_term_fires_error():
    ontology = {
        'CL:0000002': {
            'label': 'obsolete immortal cell line cell',
            'deprecated': True,
            'replaced_by': 'CLO:0000019',
        },
    }
    failures = list(audit_controlled_term_deprecated(_value('CL:0000002'), _system(ontology)))
    assert len(failures) == 1
    assert failures[0].category == CATEGORY
    assert failures[0].__json__()['level_name'] == 'ERROR'
    detail = failures[0].detail
    assert '[CL:0000002](/controlled-terms/CL:0000002/)' in detail
    assert '`CL:0000002` (obsolete immortal cell line cell), which is deprecated' in detail
    assert 'The ontology replaces it with `CLO:0000019`.' in detail


def test_deprecated_term_without_replacement():
    ontology = {'UBERON:0000027': {'label': '', 'deprecated': True}}
    failures = list(audit_controlled_term_deprecated(_value('UBERON:0000027'), _system(ontology)))
    assert len(failures) == 1
    assert '`UBERON:0000027`, which is deprecated' in failures[0].detail
    assert 'replaces it with' not in failures[0].detail


@pytest.mark.parametrize('entry', [
    {'label': 'cell', 'deprecated': False},
    {'label': 'cell'},
])
def test_current_term_no_audit(entry):
    ontology = {'CL:0000000': entry}
    assert list(audit_controlled_term_deprecated(_value('CL:0000000'), _system(ontology))) == []


def test_term_missing_from_ontology_no_audit():
    assert list(audit_controlled_term_deprecated(_value('CL:9000000'), _system({}))) == []


def test_anti_uniprot_term_uses_bare_uniprot_entry():
    ontology = {'uniprot:P00000': {'label': 'retired protein', 'deprecated': True}}
    failures = list(audit_controlled_term_deprecated(_value('anti-uniprot:P00000'), _system(ontology)))
    assert len(failures) == 1
    assert '`anti-uniprot:P00000` (retired protein), which is deprecated' in failures[0].detail


def test_deprecated_controlled_term_audit(indexer_testapp, controlled_term_deprecated):
    res = indexer_testapp.get(controlled_term_deprecated['@id'] + '@@index-data')
    errors = [error for error in res.json['audit'].get('ERROR', []) if error['category'] == CATEGORY]
    assert len(errors) == 1
    assert 'CLO:0000019' in errors[0]['detail']


def test_current_controlled_term_no_audit(indexer_testapp, controlled_term_with_definition):
    res = indexer_testapp.get(controlled_term_with_definition['@id'] + '@@index-data')
    assert not any(error['category'] == CATEGORY for error in _audit_errors(res))


def test_controlled_term_not_in_ontology_no_audit(indexer_testapp, controlled_term_with_aliases):
    res = indexer_testapp.get(controlled_term_with_aliases['@id'] + '@@index-data')
    assert not any(error['category'] == CATEGORY for error in _audit_errors(res))
