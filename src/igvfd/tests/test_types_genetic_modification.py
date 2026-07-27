import pytest


def test_genetic_modification_summary_with_description(testapp, genetic_modification_with_description):
    res = testapp.get(genetic_modification_with_description['@id'])
    assert res.json.get('summary') == 'CRISPRi-based gene silencing modification.'


def test_genetic_modification_summary_with_strategy(testapp, genetic_modification):
    res = testapp.get(genetic_modification['@id'])
    # When description is missing, summary should use strategy
    assert res.json.get('summary') == 'knockout screen'


def test_genetic_modification_summary_with_aliases(testapp, genetic_modification_with_aliases):
    res = testapp.get(genetic_modification_with_aliases['@id'])
    # Summary prioritizes strategy over aliases when description is missing
    assert res.json.get('summary') == 'cutting screen'


def test_genetic_modification_required_fields(testapp):
    # Test that strategy is required
    testapp.post_json(
        '/genetic_modification',
        {
            'description': 'A modification without strategy.',
        },
        status=422
    )


def test_genetic_modification_strategy_enum(testapp):
    # Test that only valid strategy values are allowed
    testapp.post_json(
        '/genetic_modification',
        {
            'strategy': 'invalid_strategy',
        },
        status=422
    )


def test_genetic_modification_create(testapp):
    item = {
        'strategy': 'knockout screen',
        'status': 'current',
    }
    res = testapp.post_json('/genetic_modification', item, status=201)
    assert res.json['@graph'][0]['strategy'] == 'knockout screen'


def test_genetic_modification_create_with_all_fields(testapp):
    item = {
        'strategy': 'prime editing screen',
        'description': 'Prime editing for precise insertions.',
        'aliases': ['lattice:gm-test-complete'],
        'status': 'current',
    }
    res = testapp.post_json('/genetic_modification', item, status=201)
    assert res.json['@graph'][0]['strategy'] == 'prime editing screen'
    assert res.json['@graph'][0]['description'] == 'Prime editing for precise insertions.'
    assert res.json['@graph'][0]['aliases'] == ['lattice:gm-test-complete']


def test_genetic_modification_create_knockout_mutation(testapp):
    item = {
        'strategy': 'knockout mutation',
        'status': 'current',
    }
    res = testapp.post_json('/genetic_modification', item, status=201)
    assert res.json['@graph'][0]['strategy'] == 'knockout mutation'


def test_genetic_modification_all_strategies(testapp):
    strategies = [
        'activation screen',
        'base editing screen',
        'cutting screen',
        'interference screen',
        'knockout screen',
        'localizing screen',
        'prime editing screen',
        'knockout mutation',
    ]
    for strategy in strategies:
        item = {
            'strategy': strategy,
            'status': 'current',
        }
        res = testapp.post_json('/genetic_modification', item, status=201)
        assert res.json['@graph'][0]['strategy'] == strategy


def test_genetic_modification_guide_rna_files_create(testapp, tabular_file):
    item = {
        'strategy': 'knockout screen',
        'guide_rna_files': [tabular_file['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/genetic_modification', item, status=201)
    assert res.json['@graph'][0]['guide_rna_files'] == [tabular_file['@id']]


def test_genetic_modification_guide_rna_files_min_items(testapp):
    testapp.post_json(
        '/genetic_modification',
        {
            'strategy': 'knockout screen',
            'guide_rna_files': [],
            'status': 'current',
        },
        status=422,
    )


def test_genetic_modification_guide_rna_files_multiple_files(
    testapp, tabular_file, tabular_file_tsv
):
    item = {
        'strategy': 'interference screen',
        'guide_rna_files': [tabular_file['@id'], tabular_file_tsv['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/genetic_modification', item, status=201)
    assert res.json['@graph'][0]['guide_rna_files'] == [
        tabular_file['@id'],
        tabular_file_tsv['@id'],
    ]


def test_genetic_modification_guide_rna_files_embed(testapp, tabular_file):
    item = {
        'strategy': 'cutting screen',
        'guide_rna_files': [tabular_file['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/genetic_modification', item, status=201)
    gm_id = res.json['@graph'][0]['@id']
    res = testapp.get(gm_id)
    embedded = res.json['guide_rna_files'][0]
    assert embedded['@id'] == tabular_file['@id']
    assert embedded['file_format'] == tabular_file['file_format']


def test_genetic_modification_targeted_genes_knockout_mutation(testapp):
    item = {
        'strategy': 'knockout mutation',
        'targeted_genes': ['TP53', 'EGFR'],
        'status': 'current',
    }
    res = testapp.post_json('/genetic_modification', item, status=201)
    assert res.json['@graph'][0]['targeted_genes'] == ['TP53', 'EGFR']


@pytest.mark.parametrize(
    'strategy',
    [
        'activation screen',
        'knockout screen',
        'interference screen',
    ],
)
def test_genetic_modification_targeted_genes_rejected_without_knockout_mutation(
    testapp, strategy
):
    testapp.post_json(
        '/genetic_modification',
        {
            'strategy': strategy,
            'targeted_genes': ['TP53'],
            'status': 'current',
        },
        status=422,
    )


def test_genetic_modification_targeted_genes_min_items(testapp):
    testapp.post_json(
        '/genetic_modification',
        {
            'strategy': 'knockout mutation',
            'targeted_genes': [],
            'status': 'current',
        },
        status=422,
    )
