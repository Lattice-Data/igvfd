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


def test_controlled_term_dbxrefs_cas_pattern_valid(testapp):
    item = {
        'term_id': 'CHEBI:99999',
        'ontology_source': 'CHEBI',
        'dbxrefs': ['CAS:50-00-0'],
        'status': 'current',
    }
    res = testapp.post_json('/controlled_term', item, status=201)
    assert res.json['@graph'][0]['dbxrefs'] == ['CAS:50-00-0']


def test_controlled_term_dbxrefs_cas_pattern_invalid(testapp):
    testapp.post_json(
        '/controlled_term',
        {
            'term_id': 'CHEBI:99998',
            'ontology_source': 'CHEBI',
            'dbxrefs': ['50-00-0'],
            'status': 'current',
        },
        status=422
    )


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


def test_controlled_term_zfs_create(testapp):
    item = {
        'term_id': 'ZFS:0000001',
        'ontology_source': 'ZFS',
        'status': 'current',
    }
    res = testapp.post_json('/controlled_term', item, status=201)
    graph = res.json['@graph'][0]
    assert graph['term_id'] == 'ZFS:0000001'
    assert graph['ontology_source'] == 'ZFS'


def test_controlled_term_aliases_accept_lattice_ontology_term(testapp):
    # lattice:<ontology>_<term>; several aliases per term, synonyms included, are allowed.
    aliases = [
        'lattice:uberon_liver', 'lattice:anti_uniprot_cd28_human', 'lattice:cvcl_k_562',
        'lattice:chebi_saha', 'lattice:hsapdv_80_year_old_and_over_stage',
    ]
    item = {'term_id': 'CL:1000015', 'ontology_source': 'CL', 'aliases': aliases, 'status': 'current'}
    res = testapp.post_json('/controlled_term', item, status=201)
    assert res.json['@graph'][0]['aliases'] == aliases


@pytest.mark.parametrize(
    'alias',
    [
        # Lab prefixes the shared aliases rule accepts on other types.
        'will-allen:uberon_liver',
        'teri-klein:uberon_liver',
        # Only lowercase letters, digits and single underscores after the prefix.
        'lattice:UBERON_liver',
        'lattice:uberon-liver',
        'lattice:uberon liver',
        'lattice:uberon__liver',
        'lattice:uberon_liver_',
        'lattice:_uberon_liver',
        "lattice:efo_10x_5'_v3",
        # The ontology part and at least one term part, separated by an underscore.
        'lattice:liver',
        'lattice:',
        'Lattice:uberon_liver',
        # Anchored at true end of input, and no surrounding whitespace.
        'lattice:uberon_liver\n',
        ' lattice:uberon_liver',
        'lattice:uberon_liver ',
    ],
)
def test_controlled_term_aliases_reject_other_forms(testapp, alias):
    item = {'term_id': 'CL:1000021', 'ontology_source': 'CL', 'aliases': [alias], 'status': 'current'}
    res = testapp.post_json('/controlled_term', item, status=422)
    assert any(error.get('name') == ['aliases', 0] for error in res.json['errors']), repr(alias)


def test_controlled_term_aliases_pattern_is_controlled_term_only(registry):
    # The narrower rule is a ControlledTerm override; other types keep the shared lab-prefix rule.
    from snovault import TYPES

    types = registry[TYPES]
    assert types['controlled_term'].schema['properties']['aliases']['items']['pattern'] != (
        types['lab'].schema['properties']['aliases']['items']['pattern']
    )
    assert types['controlled_term'].schema['properties']['aliases']['items']['uniqueKey'] == 'alias'
    assert types['controlled_term'].schema['properties']['aliases']['minItems'] == 1


def test_controlled_term_dbxrefs_rejects_surrounding_whitespace(testapp):
    # The pattern ends with `(?![\s\S])`, so it anchors at true end of input. With `$`
    # alone a trailing newline validated under Python `re` while ECMA-262 rejected it,
    # and uniqueItems treated the two strings as distinct entries on one object.
    base = {'term_id': 'CHEBI:99997', 'ontology_source': 'CHEBI', 'status': 'current'}
    res = testapp.post_json('/controlled_term', {**base, 'dbxrefs': ['PMID:12345678']}, status=201)
    at_id = res.json['@graph'][0]['@id']
    for bad in ['PMID:12345678\n', 'PMID:12345678\n\n', ' PMID:12345678',
                'PMID:12345678 ', 'PMID:12345678x']:
        testapp.patch_json(at_id, {'dbxrefs': [bad]}, status=422)


def test_controlled_term_dbxrefs_rejects_empty_array(testapp):
    testapp.post_json(
        '/controlled_term',
        {'term_id': 'CHEBI:99996', 'ontology_source': 'CHEBI', 'dbxrefs': [], 'status': 'current'},
        status=422,
    )


def test_controlled_term_dbxrefs_rejects_duplicates(testapp):
    testapp.post_json(
        '/controlled_term',
        {
            'term_id': 'CHEBI:99995',
            'ontology_source': 'CHEBI',
            'dbxrefs': ['PMID:12345678', 'PMID:12345678'],
            'status': 'current',
        },
        status=422,
    )


def test_controlled_term_dbxrefs_patch(testapp):
    base = {'term_id': 'CHEBI:99994', 'ontology_source': 'CHEBI', 'status': 'current'}
    res = testapp.post_json('/controlled_term', base, status=201)
    at_id = res.json['@graph'][0]['@id']
    patched = testapp.patch_json(at_id, {'dbxrefs': ['CAS:50-00-0']}, status=200)
    assert patched.json['@graph'][0]['dbxrefs'] == ['CAS:50-00-0']
    testapp.patch_json(at_id, {'dbxrefs': ['50-00-0']}, status=422)
    testapp.patch_json(at_id, {'dbxrefs': []}, status=422)


@pytest.mark.parametrize('term_id, expected', [
    ('anti-uniprot:P01308', ('anti-', 'uniprot:P01308')),
    ('uniprot:P01308', ('', 'uniprot:P01308')),
    ('CL:0000000', ('', 'CL:0000000')),
])
def test_split_antibody_prefix(term_id, expected):
    from igvfd.types.controlled_term import split_antibody_prefix
    assert split_antibody_prefix(term_id) == expected
