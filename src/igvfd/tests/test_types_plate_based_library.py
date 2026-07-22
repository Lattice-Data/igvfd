import pytest


def test_plate_based_library_summary_with_aliases(testapp, plate_based_library_with_aliases):
    res = testapp.get(plate_based_library_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:pytest-plate-library-basic'


def test_plate_based_library_summary_with_description(testapp, plate_based_library_with_description):
    res = testapp.get(plate_based_library_with_description['@id'])
    assert res.json.get('summary') == 'Test plate-based library'


def test_plate_based_library_summary_with_uuid(testapp, plate_based_library):
    res = testapp.get(plate_based_library['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


def test_plate_based_library_required_fields(testapp, other_lab, tissue):
    # Missing lab
    testapp.post_json(
        '/plate_based_library',
        {
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
        },
        status=422
    )
    # Missing samples
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'library_cardinality': 'single',
        },
        status=422
    )
    # Missing library_cardinality
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
        },
        status=422
    )


def test_plate_based_library_feature_types_min_items(testapp, other_lab, tissue):
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
            'feature_types': [],
            'status': 'current',
        },
        status=422
    )


def test_plate_based_library_feature_types_enum(testapp, other_lab, tissue):
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
            'feature_types': ['ATAC'],
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize(
    'feature_type',
    [
        'Gene Expression',
        'Multiplexing Capture',
        'CRISPR Guide Capture',
    ]
)
def test_plate_based_library_create_with_feature_type_enum_values(
    testapp, other_lab, tissue, feature_type
):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'feature_types': [feature_type],
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
    assert res.json['@graph'][0]['feature_types'] == [feature_type]


def test_plate_based_library_multiplexing_method_requires_two_samples(testapp, other_lab, tissue):
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
            'multiplexing_method': ['combinatorial indexing'],
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize(
    'multiplexing_method',
    [
        'antibody hashing',
        'lipid hashing',
        'chemical hashing',
        'probe barcoding',
        'natural genetic variation',
        'combinatorial indexing',
    ]
)
def test_plate_based_library_create_with_multiplexing_method_enum_values(
    testapp, other_lab, tissue, tissue_with_aliases, multiplexing_method
):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id'], tissue_with_aliases['@id']],
        'library_cardinality': 'single',
        'multiplexing_method': [multiplexing_method],
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
    assert res.json['@graph'][0]['multiplexing_method'] == [multiplexing_method]


def test_plate_based_library_create_success(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
    assert res.json['@graph'][0]['lab'] == other_lab['@id']
    assert res.json['@graph'][0]['samples'] == [tissue['@id']]


def test_plate_based_library_dbxrefs_valid(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'dbxrefs': ['EGA:EGAX12345', 'GEO:GSM67890'],
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
    assert res.json['@graph'][0]['dbxrefs'] == ['EGA:EGAX12345', 'GEO:GSM67890']


def test_plate_based_library_dbxrefs_invalid(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'dbxrefs': ['BioSample:SAMEA1234567'],
        'status': 'current',
    }
    testapp.post_json('/plate_based_library', item, status=422)


@pytest.mark.parametrize(
    'cro_group_identifier',
    [
        'CRO-BATCH-2024-01',
        'x',
        'group_A-1',
    ]
)
def test_plate_based_library_cro_group_identifier_valid(testapp, other_lab, tissue, cro_group_identifier):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'CRO_group_identifier': cro_group_identifier,
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
    assert res.json['@graph'][0]['CRO_group_identifier'] == cro_group_identifier


@pytest.mark.parametrize(
    'cro_group_identifier',
    [
        '',
        ' padded ',
    ]
)
def test_plate_based_library_cro_group_identifier_invalid(testapp, other_lab, tissue, cro_group_identifier):
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
            'CRO_group_identifier': cro_group_identifier,
            'status': 'current',
        },
        status=422,
    )


def test_plate_based_library_create_with_all_optional_fields(
    testapp, other_lab, tissue, tissue_with_aliases
):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id'], tissue_with_aliases['@id']],
        'library_cardinality': 'single',
        'feature_types': ['Gene Expression', 'Multiplexing Capture'],
        'multiplexing_method': ['antibody hashing'],
        'description': 'Complete plate-based library',
        'CRO_group_identifier': 'PLATE-CRO-42',
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
    assert res.json['@graph'][0]['feature_types'] == ['Gene Expression', 'Multiplexing Capture']
    assert res.json['@graph'][0]['multiplexing_method'] == ['antibody hashing']
    assert res.json['@graph'][0]['description'] == 'Complete plate-based library'
    assert res.json['@graph'][0]['CRO_group_identifier'] == 'PLATE-CRO-42'


def test_plate_based_library_author_metadata(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'author_metadata': {
            'library_batch': 'PL-42',
            'plate_id': 'P001',
        },
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
    assert res.json['@graph'][0]['author_metadata'] == item['author_metadata']


def test_plate_based_library_patch_library_construction_technology(
    testapp, plate_based_library, controlled_term_efo
):
    res = testapp.patch_json(
        plate_based_library['@id'],
        {'library_construction_technology': controlled_term_efo['@id']},
        status=200,
    )
    assert res.json['@graph'][0]['library_construction_technology'] == controlled_term_efo['@id']


def test_plate_based_library_create_with_library_construction_technology(
    testapp, plate_based_library_with_library_construction_technology, controlled_term_efo
):
    res = testapp.get(plate_based_library_with_library_construction_technology['@id'])
    assert res.json['library_construction_technology']['@id'] == controlled_term_efo['@id']


def test_plate_based_library_linked_libraries_min_items(testapp, other_lab, tissue):
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'dual',
            'linked_libraries': [],
            'status': 'current',
        },
        status=422
    )


def test_plate_based_library_linked_libraries_unique_items(testapp, other_lab, tissue, plate_based_library):
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'dual',
            'linked_libraries': [plate_based_library['@id'], plate_based_library['@id']],
            'status': 'current',
        },
        status=422
    )


def test_plate_based_library_linked_libraries_linkto_validation(
    testapp, other_lab, tissue, droplet_based_library
):
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'dual',
            'linked_libraries': [droplet_based_library['@id']],
            'status': 'current',
        },
        status=422
    )


def test_plate_based_library_create_with_linked_libraries(testapp, other_lab, tissue, plate_based_library):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'dual',
        'linked_libraries': [plate_based_library['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
    assert res.json['@graph'][0]['linked_libraries'] == [plate_based_library['@id']]


def test_plate_based_library_create_with_multiple_linked_libraries(
    testapp,
    other_lab,
    tissue,
    plate_based_library,
    plate_based_library_with_feature_types,
):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'dual',
        'linked_libraries': [
            plate_based_library['@id'],
            plate_based_library_with_feature_types['@id'],
        ],
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
    assert len(res.json['@graph'][0]['linked_libraries']) == 2
    assert plate_based_library['@id'] in res.json['@graph'][0]['linked_libraries']
    assert plate_based_library_with_feature_types['@id'] in res.json['@graph'][0]['linked_libraries']


def test_plate_based_library_linked_libraries_requires_dual_cardinality(
    testapp, other_lab, tissue, plate_based_library
):
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'library_cardinality': 'single',
            'linked_libraries': [plate_based_library['@id']],
            'status': 'current',
        },
        status=422
    )


def test_plate_based_library_linked_libraries_with_dual_cardinality_succeeds(
    testapp, other_lab, tissue, plate_based_library
):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'dual',
        'linked_libraries': [plate_based_library['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
    assert res.json['@graph'][0]['library_cardinality'] == 'dual'
    assert res.json['@graph'][0]['linked_libraries'] == [plate_based_library['@id']]


def test_plate_based_library_single_cardinality_without_linked_libraries_succeeds(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'library_cardinality': 'single',
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
    assert res.json['@graph'][0]['library_cardinality'] == 'single'
    assert 'linked_libraries' not in res.json['@graph'][0] or res.json['@graph'][0].get('linked_libraries') is None


def test_plate_based_library_guide_rna_files_with_crispr_guide_capture(
    testapp, other_lab, tissue, tabular_file
):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'feature_types': ['CRISPR Guide Capture'],
        'guide_rna_files': [tabular_file['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
    assert res.json['@graph'][0]['guide_rna_files'] == [tabular_file['@id']]


@pytest.mark.parametrize(
    'feature_types',
    [
        ['Gene Expression'],
        ['Multiplexing Capture'],
        ['Gene Expression', 'Multiplexing Capture'],
    ]
)
def test_plate_based_library_guide_rna_files_rejected_without_crispr_guide_capture(
    testapp, other_lab, tissue, tabular_file, feature_types
):
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'feature_types': feature_types,
            'guide_rna_files': [tabular_file['@id']],
            'status': 'current',
        },
        status=422,
    )


def test_plate_based_library_guide_rna_files_max_items(
    testapp, other_lab, tissue, tabular_file, tabular_file_tsv
):
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'feature_types': ['CRISPR Guide Capture'],
            'guide_rna_files': [tabular_file['@id'], tabular_file_tsv['@id']],
            'status': 'current',
        },
        status=422,
    )
