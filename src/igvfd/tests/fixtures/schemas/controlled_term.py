import pytest


@pytest.fixture
def controlled_term(testapp):
    item = {
        'term_id': 'CL:0000005',
        'ontology_source': 'CL',
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_with_definition(testapp):
    item = {
        'term_id': 'CL:0000000',
        'ontology_source': 'CL',
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_with_synonyms(testapp):
    item = {
        'term_id': 'CL:0000001',
        'ontology_source': 'CL',
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_with_aliases(testapp):
    item = {
        'term_id': 'CL:9000000',
        'ontology_source': 'CL',
        'aliases': ['lattice:test-term-1', 'lattice:test-term-alias'],
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_uuid_summary(testapp):
    item = {
        'term_id': 'CL:9000001',
        'ontology_source': 'CL',
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_efo(testapp):
    item = {
        'term_id': 'EFO:0000001',
        'ontology_source': 'EFO',
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_ethnicity(testapp):
    item = {
        'term_id': 'EFO:0000002',
        'ontology_source': 'EFO',
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_dev_stage_human(testapp):
    item = {
        'term_id': 'HsapDv:0000002',
        'ontology_source': 'HsapDv',
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_brain(testapp):
    item = {
        'term_id': 'UBERON:0000955',
        'ontology_source': 'UBERON',
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_hancestro(testapp):
    item = {
        'term_id': 'HANCESTRO:0304',
        'ontology_source': 'HANCESTRO',
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_chebi(testapp):
    item = {
        'term_id': 'CHEBI:15377',
        'ontology_source': 'CHEBI',
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]


@pytest.fixture
def controlled_term_uniprot(testapp):
    item = {
        'term_id': 'uniprot:P01308',
        'ontology_source': 'UniProt',
        'status': 'current',
    }
    return testapp.post_json('/controlled_term', item, status=201).json['@graph'][0]
