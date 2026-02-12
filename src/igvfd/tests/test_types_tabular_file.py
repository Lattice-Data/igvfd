import pytest


def test_tabular_file_summary_with_aliases(testapp, tabular_file_with_aliases):
    res = testapp.get(tabular_file_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:tabular-file-001'


def test_tabular_file_summary_with_description(testapp, tabular_file_with_description):
    res = testapp.get(tabular_file_with_description['@id'])
    assert res.json.get('summary') == 'Test tabular file'


def test_tabular_file_summary_with_uuid(testapp, tabular_file):
    res = testapp.get(tabular_file['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


def test_tabular_file_required_fields(testapp, other_lab):
    # Missing lab
    testapp.post_json(
        '/tabular_file',
        {
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            'file_format': 'csv',
            's3_uri': 's3://lattice-test-data/tabular/required-lab.csv',
        },
        status=422
    )
    # Missing md5sum
    testapp.post_json(
        '/tabular_file',
        {
            'lab': other_lab['@id'],
            'file_format': 'csv',
            's3_uri': 's3://lattice-test-data/tabular/required-md5sum.csv',
        },
        status=422
    )
    # Missing file_format
    testapp.post_json(
        '/tabular_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            's3_uri': 's3://lattice-test-data/tabular/required-format.csv',
        },
        status=422
    )


def test_tabular_file_file_format_enum(testapp, other_lab):
    testapp.post_json(
        '/tabular_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            'file_format': 'invalid_format',
            's3_uri': 's3://lattice-test-data/tabular/invalid-format.csv',
            'status': 'current',
        },
        status=422
    )


def test_tabular_file_md5sum_pattern(testapp, other_lab):
    # Invalid md5sum pattern (too short)
    testapp.post_json(
        '/tabular_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'abc123',
            'file_format': 'csv',
            's3_uri': 's3://lattice-test-data/tabular/invalid-md5sum-short.csv',
            'status': 'current',
        },
        status=422
    )
    # Invalid md5sum pattern (invalid characters)
    testapp.post_json(
        '/tabular_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz',
            'file_format': 'csv',
            's3_uri': 's3://lattice-test-data/tabular/invalid-md5sum-chars.csv',
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize(
    'file_format',
    [
        'csv',
        'tsv',
    ]
)
def test_tabular_file_create_with_file_format_enum_values(testapp, other_lab, file_format):
    item = {
        'lab': other_lab['@id'],
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': file_format,
        's3_uri': f's3://lattice-test-data/tabular/enum-{file_format}.dat',
        'status': 'current',
    }
    res = testapp.post_json('/tabular_file', item, status=201)
    assert res.json['@graph'][0]['file_format'] == file_format


def test_tabular_file_create_success(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'csv',
        's3_uri': 's3://lattice-test-data/tabular/create-success.csv',
        'status': 'current',
    }
    res = testapp.post_json('/tabular_file', item, status=201)
    assert res.json['@graph'][0]['lab'] == other_lab['@id']
    assert res.json['@graph'][0]['md5sum'] == '74b87337454200d4d33f80c4663dc5e5'
    assert res.json['@graph'][0]['file_format'] == 'csv'
    assert res.json['@graph'][0]['s3_uri'] == 's3://lattice-test-data/tabular/create-success.csv'


def test_tabular_file_create_with_all_optional_fields(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'csv',
        's3_uri': 's3://lattice-test-data/tabular/all-optional.csv',
        'file_size': 1024000,
        'description': 'Test tabular file with all fields',
        'status': 'current',
    }
    res = testapp.post_json('/tabular_file', item, status=201)
    assert res.json['@graph'][0]['file_size'] == 1024000
    assert res.json['@graph'][0]['description'] == 'Test tabular file with all fields'


def test_tabular_file_file_size_minimum(testapp, other_lab):
    testapp.post_json(
        '/tabular_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            'file_format': 'csv',
            's3_uri': 's3://lattice-test-data/tabular/invalid-filesize.csv',
            'file_size': -1,
            'status': 'current',
        },
        status=422
    )


def test_tabular_file_requires_s3_uri_when_file_available(testapp, other_lab):
    testapp.post_json(
        '/tabular_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '11111111111111111111111111111111',
            'file_format': 'csv',
            'status': 'current',
        },
        status=422
    )


def test_tabular_file_accepts_no_file_available_without_s3_uri(testapp, other_lab):
    res = testapp.post_json(
        '/tabular_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '22222222222222222222222222222222',
            'file_format': 'csv',
            'no_file_available': True,
            'status': 'current',
        },
        status=201
    )
    assert res.json['@graph'][0]['no_file_available'] is True


def test_tabular_file_rejects_s3_uri_when_no_file_available_true(testapp, other_lab):
    testapp.post_json(
        '/tabular_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '33333333333333333333333333333333',
            'file_format': 'csv',
            's3_uri': 's3://lattice-test-data/tabular/conflict.csv',
            'no_file_available': True,
            'status': 'current',
        },
        status=422
    )


def test_tabular_file_rejects_non_s3_uri_prefix(testapp, other_lab):
    testapp.post_json(
        '/tabular_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '44444444444444444444444444444444',
            'file_format': 'csv',
            's3_uri': 'https://bucket/path/file.csv',
            'status': 'current',
        },
        status=422
    )
