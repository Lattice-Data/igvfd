import pytest


def test_plate_based_library_summary_with_aliases(testapp, plate_based_library_with_aliases):
    res = testapp.get(plate_based_library_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:plate-library-basic'


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
        },
        status=422
    )
    # Missing samples
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
        },
        status=422
    )


def test_plate_based_library_kit_version_enum(testapp, other_lab, tissue):
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'kit_version': 'invalid_kit',
            'status': 'current',
        },
        status=422
    )


def test_plate_based_library_indexing_rounds_minimum(testapp, other_lab, tissue):
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'indexing_rounds': 1,
            'status': 'current',
        },
        status=422
    )


def test_plate_based_library_indexing_rounds_maximum(testapp, other_lab, tissue):
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'indexing_rounds': 5,
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize(
    'kit_version',
    [
        'QuantumScale Single Cell RNA',
        'sci-RNA-seq3'
    ]
)
def test_plate_based_library_create_with_kit_version_enum_values(testapp, other_lab, tissue, kit_version):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'kit_version': kit_version,
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
    assert res.json['@graph'][0]['kit_version'] == kit_version


@pytest.mark.parametrize(
    'indexing_rounds',
    [2, 3, 4]
)
def test_plate_based_library_create_with_indexing_rounds_values(testapp, other_lab, tissue, indexing_rounds):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'indexing_rounds': indexing_rounds,
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
    assert res.json['@graph'][0]['indexing_rounds'] == indexing_rounds


def test_plate_based_library_create_success(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
    assert res.json['@graph'][0]['lab'] == other_lab['@id']
    assert res.json['@graph'][0]['samples'] == [tissue['@id']]


def test_plate_based_library_create_with_all_optional_fields(testapp, other_lab, tissue):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'kit_version': 'QuantumScale Single Cell RNA',
        'indexing_rounds': 3,
        'multiplexing_method': 'cell hashing',
        'description': 'Complete plate-based library',
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
    assert res.json['@graph'][0]['kit_version'] == 'QuantumScale Single Cell RNA'
    assert res.json['@graph'][0]['indexing_rounds'] == 3
    assert res.json['@graph'][0]['multiplexing_method'] == 'cell hashing'
    assert res.json['@graph'][0]['description'] == 'Complete plate-based library'


@pytest.mark.parametrize(
    'cro_order',
    [
        'AN00012345',
        'NVUS123456789-01',
    ]
)
def test_plate_based_library_create_with_cro_order(testapp, other_lab, tissue, cro_order):
    item = {
        'lab': other_lab['@id'],
        'samples': [tissue['@id']],
        'CRO_order': cro_order,
        'status': 'current',
    }
    res = testapp.post_json('/plate_based_library', item, status=201)
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
def test_plate_based_library_cro_order_invalid_pattern(testapp, other_lab, tissue, cro_order):
    testapp.post_json(
        '/plate_based_library',
        {
            'lab': other_lab['@id'],
            'samples': [tissue['@id']],
            'CRO_order': cro_order,
            'status': 'current',
        },
        status=422
    )
