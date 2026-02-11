import pytest


def test_sequencing_run_summary_with_aliases(testapp, sequencing_run_with_aliases):
    res = testapp.get(sequencing_run_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:sequencing-run-001'


def test_sequencing_run_summary_with_run_cardinality(testapp, sequencing_run_paired_end):
    res = testapp.get(sequencing_run_paired_end['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == f"paired-end run ({uuid[:8]})"


def test_sequencing_run_summary_with_uuid(testapp, other_lab, sequence_file):
    item = {
        'lab': other_lab['@id'],
        'run_cardinality': 'single-end',
        'read1': sequence_file['@id'],
        'status': 'current',
    }
    res = testapp.post_json('/sequencing_run', item, status=201)
    run = testapp.get(res.json['@graph'][0]['@id'])
    uuid = run.json.get('uuid')
    assert run.json.get('summary') == uuid


def test_sequencing_run_required_fields(testapp, other_lab, sequence_file):
    # Missing lab
    testapp.post_json(
        '/sequencing_run',
        {
            'run_cardinality': 'single-end',
            'read1': sequence_file['@id'],
        },
        status=422
    )
    # Missing run_cardinality
    testapp.post_json(
        '/sequencing_run',
        {
            'lab': other_lab['@id'],
            'read1': sequence_file['@id'],
        },
        status=422
    )
    # Missing read1
    testapp.post_json(
        '/sequencing_run',
        {
            'lab': other_lab['@id'],
            'run_cardinality': 'single-end',
        },
        status=422
    )


def test_sequencing_run_cardinality_enum(testapp, other_lab, sequence_file):
    testapp.post_json(
        '/sequencing_run',
        {
            'lab': other_lab['@id'],
            'run_cardinality': 'invalid_cardinality',
            'read1': sequence_file['@id'],
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize(
    'run_cardinality',
    [
        'single-end',
        'paired-end',
        'paired-end-with-index',
        'paired-end-with-dual-index',
        'triplet',
    ]
)
def test_sequencing_run_cardinality_enum_values(testapp, other_lab, sequence_file,
                                                sequence_file_with_description,
                                                sequence_file_with_aliases,
                                                sequence_file_cram, run_cardinality):
    # Build item based on cardinality
    item = {
        'lab': other_lab['@id'],
        'run_cardinality': run_cardinality,
        'read1': sequence_file['@id'],
        'status': 'current',
    }

    if run_cardinality in ['paired-end', 'paired-end-with-index', 'paired-end-with-dual-index', 'triplet']:
        item['read2'] = sequence_file_with_description['@id']

    if run_cardinality in ['paired-end-with-index', 'paired-end-with-dual-index']:
        item['index1'] = sequence_file_with_aliases['@id']

    if run_cardinality == 'paired-end-with-dual-index':
        item['index2'] = sequence_file_cram['@id']

    if run_cardinality == 'triplet':
        item['read3'] = sequence_file_with_aliases['@id']

    res = testapp.post_json('/sequencing_run', item, status=201)
    assert res.json['@graph'][0]['run_cardinality'] == run_cardinality


def test_sequencing_run_paired_end_requires_read2(testapp, other_lab, sequence_file):
    # paired-end should fail without read2
    testapp.post_json(
        '/sequencing_run',
        {
            'lab': other_lab['@id'],
            'run_cardinality': 'paired-end',
            'read1': sequence_file['@id'],
            'status': 'current',
        },
        status=422
    )


def test_sequencing_run_paired_end_with_index_requires_index1(testapp, other_lab, sequence_file,
                                                              sequence_file_with_description):
    # paired-end-with-index should fail without index1
    testapp.post_json(
        '/sequencing_run',
        {
            'lab': other_lab['@id'],
            'run_cardinality': 'paired-end-with-index',
            'read1': sequence_file['@id'],
            'read2': sequence_file_with_description['@id'],
            'status': 'current',
        },
        status=422
    )


def test_sequencing_run_triplet_requires_read3(testapp, other_lab, sequence_file,
                                               sequence_file_with_description):
    # triplet should fail without read3
    testapp.post_json(
        '/sequencing_run',
        {
            'lab': other_lab['@id'],
            'run_cardinality': 'triplet',
            'read1': sequence_file['@id'],
            'read2': sequence_file_with_description['@id'],
            'status': 'current',
        },
        status=422
    )


def test_sequencing_run_platform_enum(testapp, other_lab, sequence_file):
    testapp.post_json(
        '/sequencing_run',
        {
            'lab': other_lab['@id'],
            'run_cardinality': 'single-end',
            'read1': sequence_file['@id'],
            'sequencing_platform': 'Invalid Platform',
            'status': 'current',
        },
        status=422
    )


@pytest.mark.parametrize(
    'platform',
    [
        'Illumina HiSeq 2000',
        'Illumina NextSeq 500',
        'Illumina NextSeq 1000',
    ]
)
def test_sequencing_run_platform_enum_values(testapp, other_lab, sequence_file, platform):
    item = {
        'lab': other_lab['@id'],
        'run_cardinality': 'single-end',
        'read1': sequence_file['@id'],
        'sequencing_platform': platform,
        'status': 'current',
    }
    res = testapp.post_json('/sequencing_run', item, status=201)
    assert res.json['@graph'][0]['sequencing_platform'] == platform


def test_sequencing_run_create_success(testapp, other_lab, sequence_file):
    item = {
        'lab': other_lab['@id'],
        'run_cardinality': 'single-end',
        'read1': sequence_file['@id'],
        'status': 'current',
    }
    res = testapp.post_json('/sequencing_run', item, status=201)
    assert res.json['@graph'][0]['lab'] == other_lab['@id']
    assert res.json['@graph'][0]['run_cardinality'] == 'single-end'
    assert res.json['@graph'][0]['read1'] == sequence_file['@id']


def test_sequencing_run_create_with_all_optional_fields(testapp, other_lab, sequence_file,
                                                        sequence_file_with_description):
    item = {
        'lab': other_lab['@id'],
        'run_cardinality': 'paired-end',
        'read1': sequence_file['@id'],
        'read2': sequence_file_with_description['@id'],
        'sequencing_platform': 'Illumina NextSeq 1000',
        'description': 'Test sequencing run with all fields',
        'aliases': ['lattice:test-run-001'],
        'status': 'current',
    }
    res = testapp.post_json('/sequencing_run', item, status=201)
    assert res.json['@graph'][0]['sequencing_platform'] == 'Illumina NextSeq 1000'
    assert res.json['@graph'][0]['description'] == 'Test sequencing run with all fields'
    assert 'lattice:test-run-001' in res.json['@graph'][0]['aliases']
