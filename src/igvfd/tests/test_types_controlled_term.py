import pytest


def test_controlled_term_summary_with_term_name(testapp, controlled_term):
    res = testapp.get(controlled_term['@id'])
    assert res.json.get('summary') == 'test cell type'


def test_controlled_term_summary_with_aliases(testapp, controlled_term_with_aliases):
    res = testapp.get(controlled_term_with_aliases['@id'])
    # Summary prioritizes term_name over aliases, so it returns term_name
    assert res.json.get('summary') == 'test cell type with aliases'


def test_controlled_term_summary_with_uuid(testapp, controlled_term):
    res = testapp.get(controlled_term['@id'])
    uuid = res.json.get('uuid')
    # When term_name is present, it should be used instead of UUID
    assert res.json.get('summary') == 'test cell type'
    # If term_name were missing, UUID would be used
    assert uuid is not None


def test_controlled_term_required_fields(testapp):
    # Test that term_id is required
    testapp.post_json(
        '/controlled_term',
        {
            'term_name': 'test term',
            'ontology_source': 'CL',
        },
        status=422
    )
    # Test that term_name is required
    testapp.post_json(
        '/controlled_term',
        {
            'term_id': 'CL:0000000',
            'ontology_source': 'CL',
        },
        status=422
    )
    # Test that ontology_source is required
    testapp.post_json(
        '/controlled_term',
        {
            'term_id': 'CL:0000000',
            'term_name': 'test term',
        },
        status=422
    )


def test_controlled_term_ontology_source_enum(testapp):
    # Test that only valid ontology sources are allowed
    testapp.post_json(
        '/controlled_term',
        {
            'term_id': 'INVALID:0000000',
            'term_name': 'test term',
            'ontology_source': 'INVALID',
        },
        status=422
    )


def test_controlled_term_term_id_pattern(testapp):
    # Test that term_id must match pattern
    testapp.post_json(
        '/controlled_term',
        {
            'term_id': 'invalid-format',
            'term_name': 'test term',
            'ontology_source': 'CL',
        },
        status=422
    )


def test_controlled_term_create(testapp):
    item = {
        'term_id': 'CL:0000004',
        'term_name': 'test cell type',
        'ontology_source': 'CL',
        'status': 'current',
    }
    res = testapp.post_json('/controlled_term', item, status=201)
    assert res.json['@graph'][0]['term_id'] == 'CL:0000004'
    assert res.json['@graph'][0]['term_name'] == 'test cell type'
    assert res.json['@graph'][0]['ontology_source'] == 'CL'


def test_controlled_term_with_all_fields(testapp):
    item = {
        'term_id': 'CL:0000005',
        'term_name': 'complete test term',
        'ontology_source': 'CL',
        'definition': 'A complete definition.',
        'synonyms': ['syn1', 'syn2'],
        'dbxrefs': ['PMID:12345678', 'DOI:10.1234/test'],
        'status': 'current',
    }
    res = testapp.post_json('/controlled_term', item, status=201)
    assert res.json['@graph'][0]['definition'] == 'A complete definition.'
    assert res.json['@graph'][0]['synonyms'] == ['syn1', 'syn2']
    assert res.json['@graph'][0]['dbxrefs'] == ['PMID:12345678', 'DOI:10.1234/test']


def test_controlled_term_hancestro_create(testapp):
    item = {
        'term_id': 'HANCESTRO:0000001',
        'term_name': 'Han Chinese',
        'ontology_source': 'HANCESTRO',
        'status': 'current',
    }
    res = testapp.post_json('/controlled_term', item, status=201)
    assert res.json['@graph'][0]['term_id'] == 'HANCESTRO:0000001'
    assert res.json['@graph'][0]['ontology_source'] == 'HANCESTRO'


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
        'term_name': f'test term with alias prefix {prefix}',
        'ontology_source': 'CL',
        'aliases': [f'{prefix}:test-alias'],
        'status': 'current',
    }
    res = testapp.post_json('/controlled_term', item, status=201)
    assert res.json['@graph'][0]['aliases'] == item['aliases']
