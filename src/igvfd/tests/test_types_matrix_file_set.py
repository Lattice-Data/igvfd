import pytest


def test_matrix_file_set_summary_with_aliases(testapp, matrix_file_set_with_aliases):
    res = testapp.get(matrix_file_set_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:matrix-file-set-001'


def test_matrix_file_set_summary_with_description(testapp, matrix_file_set_with_all_fields):
    res = testapp.get(matrix_file_set_with_all_fields['@id'])
    # aliases take priority over description
    assert res.json.get('summary') == 'lattice:matrix-file-set-full-001'


def test_matrix_file_set_summary_with_uuid(testapp, matrix_file_set):
    res = testapp.get(matrix_file_set['@id'])
    uuid = res.json.get('uuid')
    # No aliases or description, so summary falls back to uuid
    assert res.json.get('summary') == uuid


def test_matrix_file_set_required_fields(testapp, other_lab, raw_matrix_file):
    # Missing lab
    testapp.post_json(
        '/matrix_file_set',
        {
            'raw_matrix_files': [raw_matrix_file['@id']],
        },
        status=422
    )


def test_matrix_file_set_success_with_raw_files(testapp, other_lab, raw_matrix_file,
                                                sequence_file_set_illumina_single_end):
    item = {
        'lab': other_lab['@id'],
        'raw_matrix_files': [raw_matrix_file['@id']],
        'source_sequence_file_sets': [sequence_file_set_illumina_single_end['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/matrix_file_set', item, status=201)
    assert raw_matrix_file['@id'] in res.json['@graph'][0]['raw_matrix_files']
    assert sequence_file_set_illumina_single_end['@id'] in res.json['@graph'][0]['source_sequence_file_sets']


def test_matrix_file_set_success_with_processed_files(testapp, other_lab, processed_matrix_file,
                                                      sequence_file_set_illumina_single_end):
    item = {
        'lab': other_lab['@id'],
        'processed_matrix_files': [processed_matrix_file['@id']],
        'source_sequence_file_sets': [sequence_file_set_illumina_single_end['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/matrix_file_set', item, status=201)
    assert processed_matrix_file['@id'] in res.json['@graph'][0]['processed_matrix_files']


def test_matrix_file_set_success_minimal(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'status': 'current',
    }
    res = testapp.post_json('/matrix_file_set', item, status=201)
    assert res.json['@graph'][0]['lab'] == other_lab['@id']


def test_matrix_file_set_genome_assembly_enum(testapp, other_lab):
    testapp.post_json(
        '/matrix_file_set',
        {
            'lab': other_lab['@id'],
            'genome_assembly': 'invalid_assembly',
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize(
    'genome_assembly',
    [
        'GRCh38',
        'GRCm39',
    ]
)
def test_matrix_file_set_genome_assembly_values(testapp, other_lab, genome_assembly):
    item = {
        'lab': other_lab['@id'],
        'genome_assembly': genome_assembly,
        'status': 'current',
    }
    res = testapp.post_json('/matrix_file_set', item, status=201)
    assert res.json['@graph'][0]['genome_assembly'] == genome_assembly


def test_matrix_file_set_raw_matrix_file_linkto_validation(testapp, other_lab):
    testapp.post_json(
        '/matrix_file_set',
        {
            'lab': other_lab['@id'],
            'raw_matrix_files': ['/invalid/path/'],
            'status': 'current',
        },
        status=422
    )


def test_matrix_file_set_processed_matrix_file_linkto_validation(testapp, other_lab):
    testapp.post_json(
        '/matrix_file_set',
        {
            'lab': other_lab['@id'],
            'processed_matrix_files': ['/invalid/path/'],
            'status': 'current',
        },
        status=422
    )


def test_matrix_file_set_source_sfs_linkto_validation(testapp, other_lab):
    testapp.post_json(
        '/matrix_file_set',
        {
            'lab': other_lab['@id'],
            'source_sequence_file_sets': ['/invalid/path/'],
            'status': 'current',
        },
        status=422
    )


def test_matrix_file_set_create_with_all_optional_fields(testapp, other_lab, raw_matrix_file,
                                                         processed_matrix_file,
                                                         sequence_file_set_illumina_single_end):
    item = {
        'lab': other_lab['@id'],
        'raw_matrix_files': [raw_matrix_file['@id']],
        'processed_matrix_files': [processed_matrix_file['@id']],
        'source_sequence_file_sets': [sequence_file_set_illumina_single_end['@id']],
        'software': 'Cell Ranger',
        'software_version': '7.1.0',
        'genome_assembly': 'GRCh38',
        'genome_annotation': 'GENCODE v44',
        'description': 'Test matrix file set with all fields',
        'aliases': ['lattice:test-mfs-001'],
        'status': 'current',
    }
    res = testapp.post_json('/matrix_file_set', item, status=201)
    assert res.json['@graph'][0]['software'] == 'Cell Ranger'
    assert res.json['@graph'][0]['software_version'] == '7.1.0'
    assert res.json['@graph'][0]['genome_assembly'] == 'GRCh38'
    assert res.json['@graph'][0]['genome_annotation'] == 'GENCODE v44'
    assert res.json['@graph'][0]['description'] == 'Test matrix file set with all fields'
    assert 'lattice:test-mfs-001' in res.json['@graph'][0]['aliases']
