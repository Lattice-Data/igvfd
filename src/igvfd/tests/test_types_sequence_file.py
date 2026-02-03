import pytest


def test_sequence_file_summary_with_aliases(testapp, sequence_file_with_aliases):
    res = testapp.get(sequence_file_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:sequence-file-001'


def test_sequence_file_summary_with_description(testapp, sequence_file_with_description):
    res = testapp.get(sequence_file_with_description['@id'])
    assert res.json.get('summary') == 'Test sequence file'


def test_sequence_file_summary_with_uuid(testapp, sequence_file):
    res = testapp.get(sequence_file['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == uuid


def test_sequence_file_required_fields(testapp, other_lab):
    # Missing lab
    testapp.post_json(
        '/sequence_file',
        {
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            'file_format': 'fastq',
        },
        status=422
    )
    # Missing md5sum
    testapp.post_json(
        '/sequence_file',
        {
            'lab': other_lab['@id'],
            'file_format': 'fastq',
        },
        status=422
    )
    # Missing file_format
    testapp.post_json(
        '/sequence_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        },
        status=422
    )


def test_sequence_file_file_format_enum(testapp, other_lab):
    testapp.post_json(
        '/sequence_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            'file_format': 'invalid_format',
            'status': 'current',
        },
        status=422
    )


def test_sequence_file_md5sum_pattern(testapp, other_lab):
    # Invalid md5sum pattern (too short)
    testapp.post_json(
        '/sequence_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'abc123',
            'file_format': 'fastq',
            'status': 'current',
        },
        status=422
    )
    # Invalid md5sum pattern (invalid characters)
    testapp.post_json(
        '/sequence_file',
        {
            'lab': other_lab['@id'],
            'md5sum': 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz',
            'file_format': 'fastq',
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize(
    'file_format',
    [
        'fastq',
        'cram',
    ]
)
def test_sequence_file_create_with_file_format_enum_values(testapp, other_lab, file_format):
    item = {
        'lab': other_lab['@id'],
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': file_format,
        'status': 'current',
    }
    res = testapp.post_json('/sequence_file', item, status=201)
    assert res.json['@graph'][0]['file_format'] == file_format


def test_sequence_file_create_success(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'fastq',
        'status': 'current',
    }
    res = testapp.post_json('/sequence_file', item, status=201)
    assert res.json['@graph'][0]['lab'] == other_lab['@id']
    assert res.json['@graph'][0]['md5sum'] == '74b87337454200d4d33f80c4663dc5e5'
    assert res.json['@graph'][0]['file_format'] == 'fastq'


def test_sequence_file_create_with_all_optional_fields(testapp, other_lab):
    item = {
        'lab': other_lab['@id'],
        'md5sum': '74b87337454200d4d33f80c4663dc5e5',
        'file_format': 'fastq',
        'file_size': 1024000,
        'description': 'Test sequence file with all fields',
        'status': 'current',
    }
    res = testapp.post_json('/sequence_file', item, status=201)
    assert res.json['@graph'][0]['file_size'] == 1024000
    assert res.json['@graph'][0]['description'] == 'Test sequence file with all fields'


def test_sequence_file_file_size_minimum(testapp, other_lab):
    testapp.post_json(
        '/sequence_file',
        {
            'lab': other_lab['@id'],
            'md5sum': '74b87337454200d4d33f80c4663dc5e5',
            'file_format': 'fastq',
            'file_size': -1,
            'status': 'current',
        },
        status=422
    )
