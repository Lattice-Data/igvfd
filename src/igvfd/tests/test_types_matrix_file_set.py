def test_matrix_file_set_summary_with_aliases(testapp, matrix_file_set_with_aliases):
    res = testapp.get(matrix_file_set_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:matrix-file-set-001'


def test_matrix_file_set_summary_with_description(testapp, matrix_file_set_with_all_fields):
    res = testapp.get(matrix_file_set_with_all_fields['@id'])
    assert res.json.get('summary') == 'lattice:matrix-file-set-full-001'


def test_matrix_file_set_summary_with_uuid(testapp, matrix_file_set):
    res = testapp.get(matrix_file_set['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


def test_matrix_file_set_required_fields_missing_lab(testapp, other_lab):
    testapp.post_json(
        '/matrix_file_set',
        {},
        status=422
    )


def test_matrix_file_set_success_with_raw_files(testapp, other_lab, raw_matrix_file):
    item = {
        'lab': other_lab['@id'],
        'raw_matrix_files': [raw_matrix_file['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/matrix_file_set', item, status=201)
    assert raw_matrix_file['@id'] in res.json['@graph'][0]['raw_matrix_files']


def test_matrix_file_set_success_with_processed_files(testapp, other_lab, processed_matrix_file):
    item = {
        'lab': other_lab['@id'],
        'processed_matrix_files': [processed_matrix_file['@id']],
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


def test_matrix_file_set_rejects_removed_fields(testapp, other_lab):
    testapp.post_json(
        '/matrix_file_set',
        {
            'lab': other_lab['@id'],
            'experiment_ids': ['EXP-001'],
            'status': 'current',
        },
        status=422
    )
