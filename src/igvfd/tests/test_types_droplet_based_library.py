import pytest


def test_droplet_based_library_summary_with_aliases(testapp, droplet_based_library_with_aliases):
    res = testapp.get(droplet_based_library_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:droplet-library-basic'


def test_droplet_based_library_summary_with_description(testapp, droplet_based_library_with_description):
    res = testapp.get(droplet_based_library_with_description['@id'])
    assert res.json.get('summary') == 'Test droplet-based library'


def test_droplet_based_library_summary_with_uuid(testapp, droplet_based_library):
    res = testapp.get(droplet_based_library['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


def test_droplet_based_library_required_fields(testapp, other_lab, tissue):
    # Missing lab
    testapp.post_json(
        '/droplet_based_library',
        {
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
        },
        status=422
    )
    # Missing samples
    testapp.post_json(
        '/droplet_based_library',
        {
            'lab': other_lab['@id'],
            'library_cardinality': 'single',
        },
        status=422
    )
    # Missing library_cardinality
    testapp.post_json(
        '/droplet_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
        },
        status=422
    )


def test_droplet_based_library_chemistry_version_enum(testapp, other_lab, tissue):
    testapp.post_json(
        '/droplet_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
            'chemistry_version': 'invalid_chemistry',
            'status': 'current',
        },
        status=422
    )


def test_droplet_based_library_cell_barcode_length_enum(testapp, other_lab, tissue):
    testapp.post_json(
        '/droplet_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
            'cell_barcode_length': 20,
            'status': 'current',
        },
        status=422
    )


def test_droplet_based_library_umi_length_enum(testapp, other_lab, tissue):
    testapp.post_json(
        '/droplet_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
            'umi_length': 15,
            'status': 'current',
        },
        status=422
    )


def test_droplet_based_library_feature_types_min_items(testapp, other_lab, tissue):
    testapp.post_json(
        '/droplet_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
            'feature_types': [],
            'status': 'current',
        },
        status=422
    )


def test_droplet_based_library_feature_types_unique_items(testapp, other_lab, tissue):
    testapp.post_json(
        '/droplet_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
            'feature_types': ['Gene Expression', 'Gene Expression'],
            'status': 'current',
        },
        status=422
    )


def test_droplet_based_library_feature_types_enum(testapp, other_lab, tissue):
    testapp.post_json(
        '/droplet_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
            'feature_types': ['Invalid Feature Type'],
            'status': 'current',
        },
        status=422
    )


def test_droplet_based_library_library_cardinality_enum(testapp, other_lab, tissue):
    testapp.post_json(
        '/droplet_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'invalid_cardinality',
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize(
    'chemistry_version',
    [
        "3' v2",
        "3' v3",
        "3' v3.1",
        "3' v4",
        "5' v1",
        "5' v2",
        "5' v3",
        'Multiome v1',
        'Multiome v2',
        'Flex v1',
        'Flex v2',
        'ATAC v1',
        'ATAC v2',
        'VDJ v1',
        'VDJ v2'
    ]
)
def test_droplet_based_library_create_with_chemistry_version_enum_values(testapp, other_lab, tissue, chemistry_version):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'chemistry_version': chemistry_version,
        'status': 'current',
    }
    res = testapp.post_json('/droplet_based_library', item, status=201)
    assert res.json['@graph'][0]['chemistry_version'] == chemistry_version


@pytest.mark.parametrize(
    'cell_barcode_length',
    [16, 28]
)
def test_droplet_based_library_create_with_cell_barcode_length_values(testapp, other_lab, tissue, cell_barcode_length):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'cell_barcode_length': cell_barcode_length,
        'status': 'current',
    }
    res = testapp.post_json('/droplet_based_library', item, status=201)
    assert res.json['@graph'][0]['cell_barcode_length'] == cell_barcode_length


@pytest.mark.parametrize(
    'umi_length',
    [10, 12]
)
def test_droplet_based_library_create_with_umi_length_values(testapp, other_lab, tissue, umi_length):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'umi_length': umi_length,
        'status': 'current',
    }
    res = testapp.post_json('/droplet_based_library', item, status=201)
    assert res.json['@graph'][0]['umi_length'] == umi_length


@pytest.mark.parametrize(
    'feature_type',
    [
        'Gene Expression',
        'Antibody Capture',
        'CRISPR Guide Capture',
        'Multiplexing Capture',
        'ATAC',
        'BCR',
        'TCR'
    ]
)
def test_droplet_based_library_create_with_feature_type_enum_values(testapp, other_lab, tissue, feature_type):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'feature_types': [feature_type],
        'status': 'current',
    }
    res = testapp.post_json('/droplet_based_library', item, status=201)
    assert res.json['@graph'][0]['feature_types'] == [feature_type]


@pytest.mark.parametrize(
    'library_cardinality',
    ['single', 'dual']
)
def test_droplet_based_library_create_with_library_cardinality_enum_values(testapp, other_lab, tissue, library_cardinality):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': library_cardinality,
        'status': 'current',
    }
    res = testapp.post_json('/droplet_based_library', item, status=201)
    assert res.json['@graph'][0]['library_cardinality'] == library_cardinality


def test_droplet_based_library_create_success(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'status': 'current',
    }
    res = testapp.post_json('/droplet_based_library', item, status=201)
    assert res.json['@graph'][0]['lab'] == other_lab['@id']
    assert res.json['@graph'][0]['samples'] == [tissue['@id']]
    assert res.json['@graph'][0]['library_cardinality'] == 'single'


def test_droplet_based_library_create_with_all_optional_fields(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'dual',
        'chemistry_version': "3' v3",
        'cell_barcode_length': 16,
        'umi_length': 12,
        'feature_types': ['Gene Expression', 'ATAC'],
        'multiplexing_method': 'cell hashing',
        'description': 'Complete droplet-based library',
        'status': 'current',
    }
    res = testapp.post_json('/droplet_based_library', item, status=201)
    assert res.json['@graph'][0]['library_cardinality'] == 'dual'
    assert res.json['@graph'][0]['chemistry_version'] == "3' v3"
    assert res.json['@graph'][0]['cell_barcode_length'] == 16
    assert res.json['@graph'][0]['umi_length'] == 12
    assert res.json['@graph'][0]['feature_types'] == ['Gene Expression', 'ATAC']
    assert res.json['@graph'][0]['multiplexing_method'] == 'cell hashing'
    assert res.json['@graph'][0]['description'] == 'Complete droplet-based library'


def test_droplet_based_library_linked_libraries_min_items(testapp, other_lab, tissue):
    testapp.post_json(
        '/droplet_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
            'linked_libraries': [],
            'status': 'current',
        },
        status=422
    )


def test_droplet_based_library_linked_libraries_unique_items(testapp, other_lab, tissue, droplet_based_library):
    testapp.post_json(
        '/droplet_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
            'linked_libraries': [droplet_based_library['@id'], droplet_based_library['@id']],
            'status': 'current',
        },
        status=422
    )


def test_droplet_based_library_linked_libraries_linkto_validation(testapp, other_lab, tissue):
    testapp.post_json(
        '/droplet_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'dual',
            'linked_libraries': ['/invalid/library/path/'],
            'status': 'current',
        },
        status=422
    )


def test_droplet_based_library_create_with_linked_libraries(testapp, other_lab, tissue, droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'dual',
        'linked_libraries': [droplet_based_library['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/droplet_based_library', item, status=201)
    assert res.json['@graph'][0]['linked_libraries'] == [droplet_based_library['@id']]


def test_droplet_based_library_create_with_multiple_linked_libraries(testapp, other_lab, tissue, droplet_based_library, droplet_based_library_with_chemistry_version):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'dual',
        'linked_libraries': [
            droplet_based_library['@id'],
            droplet_based_library_with_chemistry_version['@id']
        ],
        'status': 'current',
    }
    res = testapp.post_json('/droplet_based_library', item, status=201)
    assert len(res.json['@graph'][0]['linked_libraries']) == 2
    assert droplet_based_library['@id'] in res.json['@graph'][0]['linked_libraries']
    assert droplet_based_library_with_chemistry_version['@id'] in res.json['@graph'][0]['linked_libraries']


def test_droplet_based_library_linked_libraries_requires_dual_cardinality(testapp, other_lab, tissue, droplet_based_library):
    """Test that linked_libraries requires library_cardinality to be 'dual'."""
    testapp.post_json(
        '/droplet_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
            'linked_libraries': [droplet_based_library['@id']],
            'status': 'current',
        },
        status=422
    )


def test_droplet_based_library_linked_libraries_with_dual_cardinality_succeeds(testapp, other_lab, tissue, droplet_based_library):
    """Test that linked_libraries works when library_cardinality is 'dual'."""
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'dual',
        'linked_libraries': [droplet_based_library['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/droplet_based_library', item, status=201)
    assert res.json['@graph'][0]['library_cardinality'] == 'dual'
    assert res.json['@graph'][0]['linked_libraries'] == [droplet_based_library['@id']]


def test_droplet_based_library_single_cardinality_without_linked_libraries_succeeds(testapp, other_lab, tissue):
    """Test that library_cardinality 'single' works when linked_libraries is not specified."""
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'status': 'current',
    }
    res = testapp.post_json('/droplet_based_library', item, status=201)
    assert res.json['@graph'][0]['library_cardinality'] == 'single'
    assert 'linked_libraries' not in res.json['@graph'][0] or res.json['@graph'][0].get('linked_libraries') is None


@pytest.mark.parametrize(
    'cro_order',
    [
        'AN00012345',
        'NVUS123456789-01',
    ]
)
def test_droplet_based_library_create_with_cro_order(testapp, other_lab, tissue, cro_order):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'CRO_order': cro_order,
        'status': 'current',
    }
    res = testapp.post_json('/droplet_based_library', item, status=201)
    assert res.json['@graph'][0]['CRO_order'] == cro_order


@pytest.mark.parametrize(
    'cro_order',
    [
        'INVALID123',
        '12345',
        'AN12345',
        'NV123456',
    ]
)
def test_droplet_based_library_cro_order_invalid_pattern(testapp, other_lab, tissue, cro_order):
    testapp.post_json(
        '/droplet_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
            'CRO_order': cro_order,
            'status': 'current',
        },
        status=422
    )
