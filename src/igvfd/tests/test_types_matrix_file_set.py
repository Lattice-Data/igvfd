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


def test_matrix_file_set_required_fields_missing_lab(testapp, other_lab):
    # Missing lab
    testapp.post_json(
        '/matrix_file_set',
        {
            'experiment_ids': ['EXP-001'],
        },
        status=422
    )


def test_matrix_file_set_required_fields_missing_experiment_ids(testapp, other_lab):
    # Missing experiment_ids
    testapp.post_json(
        '/matrix_file_set',
        {
            'lab': other_lab['@id'],
            'status': 'current',
        },
        status=422
    )


def test_matrix_file_set_experiment_ids_empty_array(testapp, other_lab):
    # Empty experiment_ids array should fail (minItems: 1)
    testapp.post_json(
        '/matrix_file_set',
        {
            'lab': other_lab['@id'],
            'experiment_ids': [],
            'status': 'current',
        },
        status=422
    )


def test_matrix_file_set_experiment_ids_single(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'experiment_ids': ['EXP-2026-001'],
        'status': 'current',
    }
    res = testapp.post_json('/matrix_file_set', item, status=201)
    assert res.json['@graph'][0]['experiment_ids'] == ['EXP-2026-001']


def test_matrix_file_set_experiment_ids_multiple(testapp, matrix_file_set_with_multiple_experiment_ids):
    res = testapp.get(matrix_file_set_with_multiple_experiment_ids['@id'])
    assert 'EXP-004' in res.json.get('experiment_ids')
    assert 'EXP-005' in res.json.get('experiment_ids')
    assert len(res.json.get('experiment_ids')) == 2


def test_matrix_file_set_experiment_ids_duplicate_fails(testapp, other_lab):
    # Duplicate experiment_ids should fail (uniqueItems: true)
    testapp.post_json(
        '/matrix_file_set',
        {
            'lab': other_lab['@id'],
            'experiment_ids': ['EXP-001', 'EXP-001'],
            'status': 'current',
        },
        status=422
    )


def test_matrix_file_set_success_with_raw_files(testapp, other_lab, raw_matrix_file,
                                                sequence_file_set_illumina_single_end):
    item = {
        'lab': other_lab['@id'],
        'experiment_ids': ['EXP-010'],
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
        'experiment_ids': ['EXP-011'],
        'processed_matrix_files': [processed_matrix_file['@id']],
        'source_sequence_file_sets': [sequence_file_set_illumina_single_end['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/matrix_file_set', item, status=201)
    assert processed_matrix_file['@id'] in res.json['@graph'][0]['processed_matrix_files']


def test_matrix_file_set_success_minimal(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'experiment_ids': ['EXP-MINIMAL'],
        'status': 'current',
    }
    res = testapp.post_json('/matrix_file_set', item, status=201)
    assert res.json['@graph'][0]['lab'] == other_lab['@id']
    assert res.json['@graph'][0]['experiment_ids'] == ['EXP-MINIMAL']


def test_matrix_file_set_genome_assembly_enum(testapp, other_lab):
    testapp.post_json(
        '/matrix_file_set',
        {
            'lab': other_lab['@id'],
            'experiment_ids': ['EXP-012'],
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
        'experiment_ids': ['EXP-013'],
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
            'experiment_ids': ['EXP-014'],
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
            'experiment_ids': ['EXP-015'],
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
            'experiment_ids': ['EXP-016'],
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
        'experiment_ids': ['EXP-017', 'EXP-018'],
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
    assert res.json['@graph'][0]['experiment_ids'] == ['EXP-017', 'EXP-018']
    assert res.json['@graph'][0]['software'] == 'Cell Ranger'
    assert res.json['@graph'][0]['software_version'] == '7.1.0'
    assert res.json['@graph'][0]['genome_assembly'] == 'GRCh38'
    assert res.json['@graph'][0]['genome_annotation'] == 'GENCODE v44'
    assert res.json['@graph'][0]['description'] == 'Test matrix file set with all fields'
    assert 'lattice:test-mfs-001' in res.json['@graph'][0]['aliases']
