import pytest


def test_controlled_term_summary_is_term_id(testapp, controlled_term):
    res = testapp.get(controlled_term['@id'])
    assert res.json.get('summary') == controlled_term['term_id'] == 'CL:0000005'


def test_controlled_term_summary_with_aliases(testapp, controlled_term_with_aliases):
    res = testapp.get(controlled_term_with_aliases['@id'])
    assert not res.json.get('term_name')
    assert res.json.get('summary') == 'CL:9000000'


def test_controlled_term_summary_without_ontology_label(testapp, controlled_term_uuid_summary):
    res = testapp.get(controlled_term_uuid_summary['@id'])
    assert res.json.get('uuid')
    assert not res.json.get('term_name')
    assert res.json.get('aliases') in (None, [])
    assert res.json.get('summary') == 'CL:9000001'


def test_controlled_term_required_fields(testapp):
    testapp.post_json(
        '/controlled_term',
        {
            'ontology_source': 'CL',
        },
        status=422
    )
    testapp.post_json(
        '/controlled_term',
        {
            'term_id': 'CL:0000000',
        },
        status=422
    )
    testapp.post_json(
        '/controlled_term',
        {
            'term_id': 'CL:0000000',
            'ontology_source': 'CL',
            'status': 'current',
        },
        status=201,
    )


def test_controlled_term_submitted_calculated_fields_rejected(testapp):
    testapp.post_json(
        '/controlled_term',
        {
            'term_id': 'CL:0000000',
            'ontology_source': 'CL',
            'term_name': 'disallowed',
            'status': 'current',
        },
        status=422,
    )


def test_controlled_term_ontology_source_enum(testapp):
    testapp.post_json(
        '/controlled_term',
        {
            'term_id': 'INVALID:0000000',
            'ontology_source': 'INVALID',
        },
        status=422
    )


def test_controlled_term_term_id_pattern(testapp):
    testapp.post_json(
        '/controlled_term',
        {
            'term_id': 'invalid-format',
            'ontology_source': 'CL',
        },
        status=422
    )


def test_controlled_term_create(testapp):
    item = {
        'term_id': 'CL:0000004',
        'ontology_source': 'CL',
        'status': 'current',
    }
    res = testapp.post_json('/controlled_term', item, status=201)
    graph = res.json['@graph'][0]
    assert graph['term_id'] == 'CL:0000004'
    assert graph['ontology_source'] == 'CL'


def test_controlled_term_lookup_by_term_id(testapp):
    item = {
        'term_id': 'CL:0000099',
        'ontology_source': 'CL',
        'status': 'current',
    }
    testapp.post_json('/controlled_term', item, status=201)
    res = testapp.get('/controlled_terms/CL:0000099/', status=200)
    assert res.json['term_id'] == 'CL:0000099'


def test_controlled_term_term_id_unique_conflict(testapp):
    item = {
        'term_id': 'CL:0000100',
        'ontology_source': 'CL',
        'status': 'current',
    }
    testapp.post_json('/controlled_term', item, status=201)
    testapp.post_json('/controlled_term', item, status=409)


def test_controlled_term_with_all_fields(testapp):
    item = {
        'term_id': 'CL:0000005',
        'ontology_source': 'CL',
        'dbxrefs': ['PMID:12345678', 'DOI:10.1234/test'],
        'status': 'current',
    }
    res = testapp.post_json('/controlled_term', item, status=201)
    assert res.json['@graph'][0]['dbxrefs'] == ['PMID:12345678', 'DOI:10.1234/test']


def test_controlled_term_hancestro_create(testapp):
    item = {
        'term_id': 'HANCESTRO:0304',
        'ontology_source': 'HANCESTRO',
        'status': 'current',
    }
    res = testapp.post_json('/controlled_term', item, status=201)
    graph = res.json['@graph'][0]
    assert graph['term_id'] == 'HANCESTRO:0304'
    assert graph['ontology_source'] == 'HANCESTRO'


@pytest.mark.parametrize(
    'prefix,term_id',
    [
        ('teri-klein', 'CL:1000000'),
        ('andrew-gillis', 'CL:1000001'),
        ('param-singh', 'CL:1000002'),
        ('randall-platt', 'CL:1000003'),
        ('peter-sims', 'CL:1000004'),
        ('jonathan-weissman', 'CL:1000005'),
        ('bo-wang', 'CL:1000006'),
        ('andrea-califano', 'CL:1000007'),
        ('nobuhiko-hamazaki', 'CL:1000008'),
        ('alex-marson', 'CL:1000009'),
        ('heather-marlow', 'CL:1000010'),
        ('jay-shendure', 'CL:1000011'),
        ('cole-trapnell', 'CL:1000012'),
        ('michael-ward', 'CL:1000013'),
        ('jay-thiagarajah', 'CL:1000014'),
        ('merlin-lange', 'CL:1000016'),
        ('lattice', 'CL:1000015'),
    ],
)
def test_controlled_term_alias_prefixes_allowed(testapp, prefix, term_id):
    item = {
        'term_id': term_id,
        'ontology_source': 'CL',
        'aliases': [f'{prefix}:test-alias'],
        'status': 'current',
    }
    res = testapp.post_json('/controlled_term', item, status=201)
    assert res.json['@graph'][0]['aliases'] == item['aliases']
