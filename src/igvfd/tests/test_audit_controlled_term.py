import pytest

from igvfd.audit.controlled_term import (
    audit_controlled_term_deprecated,
    audit_controlled_term_not_in_ontology,
)


CATEGORY = 'deprecated ontological term'
NOT_IN_ONTOLOGY_CATEGORY = 'unrecognized ontological term'


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
    assert 'suggests considering' not in detail


def test_deprecated_term_without_replacement():
    ontology = {'UBERON:0000027': {'label': '', 'deprecated': True}}
    failures = list(audit_controlled_term_deprecated(_value('UBERON:0000027'), _system(ontology)))
    assert len(failures) == 1
    assert '`UBERON:0000027`, which is deprecated' in failures[0].detail
    assert 'replaces it with' not in failures[0].detail
    assert 'suggests considering' not in failures[0].detail


def test_deprecated_term_consider_suggestions():
    ontology = {
        'CL:0000004': {
            'label': 'obsolete cell by organism',
            'deprecated': True,
            'consider': [
                'obo.CL_0000000',
                'http://purl.obolibrary.org/obo/UBERON_0000061',
                'CL:0001034',
                'CL:0000000',
                'obo.CL_0000003',
                'obo.BIRNLEX_1234',
                'http://purl.obolibrary.org/obo/MESH_A08.663.256',
                'hgnc.5166',
                'False',
            ],
        },
        'CL:0000000': {'label': 'cell', 'deprecated': False},
        'UBERON:0000061': {'label': 'anatomical structure'},
        'CL:0001034': {'label': 'cell in vitro', 'deprecated': False},
        'CL:0000003': {'label': 'obsolete native cell', 'deprecated': True},
    }
    failures = list(audit_controlled_term_deprecated(_value('CL:0000004'), _system(ontology)))
    assert len(failures) == 1
    detail = failures[0].detail
    assert 'replaces it with' not in detail
    assert (
        'The ontology suggests considering `CL:0000000`, `UBERON:0000061`, `CL:0001034`.'
    ) in detail


@pytest.mark.parametrize('consider', [
    ['obo.BIRNLEX_1234', 'hgnc.5166', 'False'],
    ['obo.CL_0000003'],
    [],
    None,
])
def test_deprecated_term_consider_without_usable_terms(consider):
    ontology = {
        'CL:0000004': {'label': 'obsolete cell by organism', 'deprecated': True, 'consider': consider},
        'CL:0000003': {'label': 'obsolete native cell', 'deprecated': True},
    }
    failures = list(audit_controlled_term_deprecated(_value('CL:0000004'), _system(ontology)))
    assert len(failures) == 1
    assert 'suggests considering' not in failures[0].detail


@pytest.mark.parametrize('entry', [
    {'label': 'cell', 'deprecated': False},
    {'label': 'cell'},
])
def test_current_term_no_audit(entry):
    ontology = {'CL:0000000': entry}
    assert list(audit_controlled_term_deprecated(_value('CL:0000000'), _system(ontology))) == []


def test_term_missing_from_ontology_not_deprecated():
    assert list(audit_controlled_term_deprecated(_value('CL:9000000'), _system({}))) == []


def test_anti_uniprot_term_uses_bare_uniprot_entry():
    ontology = {'uniprot:P00000': {'label': 'retired protein', 'deprecated': True}}
    failures = list(audit_controlled_term_deprecated(_value('anti-uniprot:P00000'), _system(ontology)))
    assert len(failures) == 1
    assert '`anti-uniprot:P00000` (retired protein), which is deprecated' in failures[0].detail


@pytest.mark.parametrize('term_id', ['CL:9000000', 'anti-uniprot:P00000', 'CL_0000000'])
def test_term_not_in_ontology_fires_warning(term_id):
    ontology = {'CL:0000000': {'label': 'cell'}}
    failures = list(audit_controlled_term_not_in_ontology(_value(term_id), _system(ontology)))
    assert len(failures) == 1
    assert failures[0].category == NOT_IN_ONTOLOGY_CATEGORY
    assert failures[0].__json__()['level_name'] == 'WARNING'
    detail = failures[0].detail
    assert f'[{term_id}](/controlled-terms/{term_id}/)' in detail
    assert f'`{term_id}`, which is not in the pinned ontology file' in detail
    assert 'newer than the pinned ontology version or whether the term ID is valid' in detail


@pytest.mark.parametrize('term_id, ontology_key, entry', [
    ('CL:0000000', 'CL:0000000', {'label': 'cell'}),
    ('CL:0000000', 'CL:0000000', {'label': 'obsolete cell', 'deprecated': True}),
    ('CL:0000000', 'CL:0000000', {}),
    ('anti-uniprot:P00000', 'uniprot:P00000', {'label': 'protein'}),
])
def test_term_in_ontology_no_not_in_ontology_audit(term_id, ontology_key, entry):
    ontology = {ontology_key: entry}
    assert list(audit_controlled_term_not_in_ontology(_value(term_id), _system(ontology))) == []


def test_deprecated_controlled_term_audit(indexer_testapp, controlled_term_deprecated):
    res = indexer_testapp.get(controlled_term_deprecated['@id'] + '@@index-data')
    errors = [error for error in res.json['audit'].get('ERROR', []) if error['category'] == CATEGORY]
    assert len(errors) == 1
    assert 'CLO:0000019' in errors[0]['detail']
    assert not any(error['category'] == NOT_IN_ONTOLOGY_CATEGORY for error in _audit_errors(res))


def test_deprecated_controlled_term_consider_audit(indexer_testapp, controlled_term_deprecated_with_consider):
    res = indexer_testapp.get(controlled_term_deprecated_with_consider['@id'] + '@@index-data')
    errors = [error for error in res.json['audit'].get('ERROR', []) if error['category'] == CATEGORY]
    assert len(errors) == 1
    assert 'The ontology suggests considering `CL:0000000`, `CL:0001034`.' in errors[0]['detail']


def test_current_controlled_term_no_audit(indexer_testapp, controlled_term_with_definition):
    res = indexer_testapp.get(controlled_term_with_definition['@id'] + '@@index-data')
    assert not any(
        error['category'] in (CATEGORY, NOT_IN_ONTOLOGY_CATEGORY) for error in _audit_errors(res)
    )


def test_controlled_term_not_in_ontology_audit(indexer_testapp, controlled_term_with_aliases):
    res = indexer_testapp.get(controlled_term_with_aliases['@id'] + '@@index-data')
    assert not any(error['category'] == CATEGORY for error in _audit_errors(res))
    warnings = [
        error for error in res.json['audit'].get('WARNING', [])
        if error['category'] == NOT_IN_ONTOLOGY_CATEGORY
    ]
    assert len(warnings) == 1
    assert '`CL:9000000`, which is not in the pinned ontology file' in warnings[0]['detail']
