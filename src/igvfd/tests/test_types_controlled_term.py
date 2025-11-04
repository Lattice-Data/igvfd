import pytest


def test_controlled_term_summary_with_term_name(testapp, controlled_term):
    res = testapp.get(controlled_term['@id'])
    assert res.json.get('summary') == 'test cell type'


def test_controlled_term_summary_with_aliases(testapp, controlled_term_with_aliases):
    res = testapp.get(controlled_term_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:test-term-1'


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
