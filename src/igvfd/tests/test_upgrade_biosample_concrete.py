import pytest

BIOSAMPLE_CONCRETE_TYPES = ['tissue', 'primary_cell_culture', 'organoid', 'cell_line']


@pytest.mark.parametrize('item_type', BIOSAMPLE_CONCRETE_TYPES)
@pytest.mark.parametrize(
    ('legacy_method', 'expected_methods'),
    [
        ('FACS', ['FACS']),
        ('MACS', ['MACS']),
        ('size exclusion', ['size selection']),
        ('density gradient', ['density gradient']),
        ('manual picking', ['manual selection']),
        ('microfluidics', ['microfluidics']),
    ],
)
def test_upgrade_enrichment_method_to_selection_methods(
    upgrader, item_type, legacy_method, expected_methods
):
    value = {'schema_version': '1', 'enrichment_method': legacy_method}
    result = upgrader.upgrade(item_type, value, current_version='1', target_version='2')
    assert result['schema_version'] == '2'
    assert result['selection_methods'] == expected_methods
    assert 'enrichment_method' not in result


@pytest.mark.parametrize('item_type', BIOSAMPLE_CONCRETE_TYPES)
def test_upgrade_enrichment_markers_sorted_and_signed(upgrader, item_type):
    value = {
        'schema_version': '1',
        'enrichment_markers': [
            {'marker': 'CD8', 'expression_level': 'negative'},
            {'marker': 'CD4', 'expression_level': 'positive'},
        ],
    }
    result = upgrader.upgrade(item_type, value, current_version='1', target_version='2')
    assert result['schema_version'] == '2'
    assert result['selection_markers'] == ['CD4+', 'CD8-']
    assert 'enrichment_markers' not in result


@pytest.mark.parametrize(
    ('expression_level', 'expected_token'),
    [
        ('intermediate', 'CD3+'),
        ('low', 'CD3+'),
        ('high', 'CD3+'),
        ('negative', 'CD3-'),
    ],
)
def test_upgrade_expression_levels(upgrader, expression_level, expected_token):
    value = {
        'schema_version': '1',
        'enrichment_markers': [{'marker': 'CD3', 'expression_level': expression_level}],
    }
    result = upgrader.upgrade('tissue', value, current_version='1', target_version='2')
    assert result['selection_markers'] == [expected_token]


@pytest.mark.parametrize('item_type', BIOSAMPLE_CONCRETE_TYPES)
def test_upgrade_method_and_markers(upgrader, item_type):
    value = {
        'schema_version': '1',
        'enrichment_method': 'MACS',
        'enrichment_markers': [{'marker': 'CD14', 'expression_level': 'positive'}],
    }
    result = upgrader.upgrade(item_type, value, current_version='1', target_version='2')
    assert result['selection_methods'] == ['MACS']
    assert result['selection_markers'] == ['CD14+']
    assert 'enrichment_method' not in result
    assert 'enrichment_markers' not in result


@pytest.mark.parametrize('item_type', BIOSAMPLE_CONCRETE_TYPES)
def test_upgrade_neither_legacy_field(upgrader, item_type):
    value = {'schema_version': '1'}
    result = upgrader.upgrade(item_type, value, current_version='1', target_version='2')
    assert result['schema_version'] == '2'
    assert 'selection_methods' not in result
    assert 'selection_markers' not in result


@pytest.mark.parametrize('item_type', BIOSAMPLE_CONCRETE_TYPES)
def test_upgrade_empty_enrichment_markers_list(upgrader, item_type):
    value = {'schema_version': '1', 'enrichment_markers': []}
    result = upgrader.upgrade(item_type, value, current_version='1', target_version='2')
    assert result['schema_version'] == '2'
    assert 'selection_markers' not in result


def test_upgrade_unknown_expression_level_raises(upgrader):
    value = {
        'schema_version': '1',
        'enrichment_markers': [{'marker': 'CD3', 'expression_level': 'unknown'}],
    }
    with pytest.raises(ValueError):
        upgrader.upgrade('tissue', value, current_version='1', target_version='2')


def test_upgrade_unknown_enrichment_method_still_drops_key(upgrader):
    value = {'schema_version': '1', 'enrichment_method': 'obsolete_future_method'}
    result = upgrader.upgrade('tissue', value, current_version='1', target_version='2')
    assert 'enrichment_method' not in result
    assert 'selection_methods' not in result


@pytest.mark.parametrize('item_type', BIOSAMPLE_CONCRETE_TYPES)
@pytest.mark.parametrize(
    'hash_index',
    [
        'P01-A1',
        'SCALE-A1',
        'BC001',
    ],
)
def test_upgrade_hash_index_to_multiplexing_barcodes(upgrader, item_type, hash_index):
    value = {'schema_version': '2', 'hash_index': hash_index}
    result = upgrader.upgrade(item_type, value, current_version='2', target_version='3')
    assert result['schema_version'] == '3'
    assert result['multiplexing_barcodes'] == [hash_index]
    assert 'hash_index' not in result


@pytest.mark.parametrize('item_type', BIOSAMPLE_CONCRETE_TYPES)
def test_upgrade_without_hash_index(upgrader, item_type):
    value = {'schema_version': '2'}
    result = upgrader.upgrade(item_type, value, current_version='2', target_version='3')
    assert result['schema_version'] == '3'
    assert 'multiplexing_barcodes' not in result
    assert 'hash_index' not in result


@pytest.mark.parametrize('item_type', BIOSAMPLE_CONCRETE_TYPES)
def test_upgrade_biosample_3_4_preserves_invalid_dbxrefs_in_submitter_comment(
    upgrader, item_type
):
    value = {
        'schema_version': '3',
        'dbxrefs': ['SRA:SRS12345', 'BioSample:SAMN53299868'],
        'submitter_comment': 'Existing submitter context.',
    }
    result = upgrader.upgrade(item_type, value, current_version='3', target_version='4')
    assert result['schema_version'] == '4'
    assert result['dbxrefs'] == ['SRA:SRS12345']
    assert result['submitter_comment'] == (
        'Existing submitter context. '
        'Legacy dbxrefs removed during schema upgrade: BioSample:SAMN53299868.'
    )


def test_upgrade_biosample_3_4_removes_all_invalid_dbxrefs(upgrader):
    value = {
        'schema_version': '3',
        'dbxrefs': ['BioSample:SAMN53299868', 'BioSample:SAMNA12345'],
    }
    result = upgrader.upgrade('tissue', value, current_version='3', target_version='4')
    assert 'dbxrefs' not in result
    assert result['submitter_comment'] == (
        'Legacy dbxrefs removed during schema upgrade: '
        'BioSample:SAMN53299868, BioSample:SAMNA12345.'
    )


@pytest.mark.parametrize('dbxrefs', [None, []])
def test_upgrade_biosample_3_4_without_dbxrefs_does_not_add_comment(upgrader, dbxrefs):
    value = {'schema_version': '3'}
    if dbxrefs is not None:
        value['dbxrefs'] = dbxrefs
    result = upgrader.upgrade('cell_line', value, current_version='3', target_version='4')
    assert result.get('dbxrefs') == dbxrefs
    assert 'submitter_comment' not in result
