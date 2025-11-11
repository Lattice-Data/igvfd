import pytest


@pytest.fixture
def controlled_term(testapp):
    item = {
        'term_id': 'CL:0000000',
        'term_name': 'test cell type',
        'ontology_source': 'CL',
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_with_definition(testapp):
    item = {
        'term_id': 'CL:0000001',
        'term_name': 'test cell type with definition',
        'ontology_source': 'CL',
        'definition': 'A test cell type definition.',
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_with_synonyms(testapp):
    item = {
        'term_id': 'CL:0000002',
        'term_name': 'test cell type with synonyms',
        'ontology_source': 'CL',
        'synonyms': ['synonym1', 'synonym2'],
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_with_aliases(testapp):
    item = {
        'term_id': 'CL:0000003',
        'term_name': 'test cell type with aliases',
        'ontology_source': 'CL',
        'aliases': ['lattice:test-term-1', 'lattice:test-term-alias'],
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_efo(testapp):
    item = {
        'term_id': 'EFO:0000001',
        'term_name': 'test EFO term',
        'ontology_source': 'EFO',
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_ethnicity(testapp):
    item = {
        'term_id': 'EFO:0000002',
        'term_name': 'test ethnicity term',
        'ontology_source': 'EFO',
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_brain(testapp):
    item = {
        'term_id': 'UBERON:0000955',
        'term_name': 'brain',
        'ontology_source': 'UBERON',
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]
