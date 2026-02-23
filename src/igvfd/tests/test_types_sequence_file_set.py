import pytest


def test_sequence_file_set_summary_with_aliases(testapp, sequence_file_set_with_aliases):
    res = testapp.get(sequence_file_set_with_aliases['@id'])
    assert res.json.get('summary') == 'lattice:sequence-file-set-001'


def test_sequence_file_set_summary_with_run_cardinality(testapp, sequence_file_set_illumina_paired_end):
    res = testapp.get(sequence_file_set_illumina_paired_end['@id'])
    uuid = res.json.get('uuid')
    assert res.json.get('summary') == f'paired-end file set ({uuid[:8]})'


def test_sequence_file_set_summary_with_uuid(testapp, sequence_file_set_illumina_single_end):
    res = testapp.get(sequence_file_set_illumina_single_end['@id'])
    uuid = res.json.get('uuid')
    # single-end cardinality is present, so summary uses that format
    assert res.json.get('summary') == f'single-end file set ({uuid[:8]})'


def test_sequence_file_set_required_fields(testapp, other_lab, sequence_file, droplet_based_library):
    # Missing lab
    testapp.post_json(
        '/sequence_file_set',
        {
            'library': droplet_based_library['@id'],
            'run_cardinality': 'single-end',
            'read1': sequence_file['@id'],
        },
        status=422
    )
    # Missing library
    testapp.post_json(
        '/sequence_file_set',
        {
            'lab': other_lab['@id'],
            'run_cardinality': 'single-end',
            'read1': sequence_file['@id'],
        },
        status=422
    )
    # Missing run_cardinality
    testapp.post_json(
        '/sequence_file_set',
        {
            'lab': other_lab['@id'],
            'library': droplet_based_library['@id'],
            'read1': sequence_file['@id'],
        },
        status=422
    )


def test_sequence_file_set_cardinality_enum(testapp, other_lab, sequence_file, droplet_based_library):
    testapp.post_json(
        '/sequence_file_set',
        {
            'lab': other_lab['@id'],
            'library': droplet_based_library['@id'],
            'run_cardinality': 'invalid_cardinality',
            'read1': sequence_file['@id'],
            'status': 'current',
        },
        status=422
    )


def test_sequence_file_set_illumina_single_end_success(testapp, other_lab, sequence_file, droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'library': droplet_based_library['@id'],
        'run_cardinality': 'single-end',
        'read1': sequence_file['@id'],
        'status': 'current',
    }
    res = testapp.post_json('/sequence_file_set', item, status=201)
    assert res.json['@graph'][0]['run_cardinality'] == 'single-end'
    assert res.json['@graph'][0]['read1'] == sequence_file['@id']
    assert res.json['@graph'][0]['library'] == droplet_based_library['@id']


def test_sequence_file_set_illumina_paired_end_success(testapp, other_lab, sequence_file,
                                                       sequence_file_with_description,
                                                       droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'library': droplet_based_library['@id'],
        'run_cardinality': 'paired-end',
        'read1': sequence_file['@id'],
        'read2': sequence_file_with_description['@id'],
        'status': 'current',
    }
    res = testapp.post_json('/sequence_file_set', item, status=201)
    assert res.json['@graph'][0]['run_cardinality'] == 'paired-end'
    assert res.json['@graph'][0]['read1'] == sequence_file['@id']
    assert res.json['@graph'][0]['read2'] == sequence_file_with_description['@id']


def test_sequence_file_set_paired_end_requires_read2(testapp, other_lab, sequence_file, droplet_based_library):
    testapp.post_json(
        '/sequence_file_set',
        {
            'lab': other_lab['@id'],
            'library': droplet_based_library['@id'],
            'run_cardinality': 'paired-end',
            'read1': sequence_file['@id'],
            'status': 'current',
        },
        status=422
    )


def test_sequence_file_set_paired_end_with_index_requires_index1(testapp, other_lab, sequence_file,
                                                                 sequence_file_with_description,
                                                                 droplet_based_library):
    testapp.post_json(
        '/sequence_file_set',
        {
            'lab': other_lab['@id'],
            'library': droplet_based_library['@id'],
            'run_cardinality': 'paired-end-with-index',
            'read1': sequence_file['@id'],
            'read2': sequence_file_with_description['@id'],
            'status': 'current',
        },
        status=422
    )


def test_sequence_file_set_triplet_requires_read3(testapp, other_lab, sequence_file,
                                                  sequence_file_with_description,
                                                  droplet_based_library):
    testapp.post_json(
        '/sequence_file_set',
        {
            'lab': other_lab['@id'],
            'library': droplet_based_library['@id'],
            'run_cardinality': 'triplet',
            'read1': sequence_file['@id'],
            'read2': sequence_file_with_description['@id'],
            'status': 'current',
        },
        status=422
    )


def test_sequence_file_set_ultima_untrimmed_cram_success(testapp, other_lab, sequence_file_cram,
                                                         droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'library': droplet_based_library['@id'],
        'run_cardinality': 'single-end',
        'untrimmed_cram': sequence_file_cram['@id'],
        'sequencing_platform': 'Ultima Genomics UG 100',
        'status': 'current',
    }
    res = testapp.post_json('/sequence_file_set', item, status=201)
    assert res.json['@graph'][0]['untrimmed_cram'] == sequence_file_cram['@id']


def test_sequence_file_set_ultima_trimmed_cram_success(testapp, other_lab, sequence_file_cram,
                                                       droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'library': droplet_based_library['@id'],
        'run_cardinality': 'single-end',
        'trimmed_cram': sequence_file_cram['@id'],
        'sequencing_platform': 'Ultima Genomics UG 100',
        'status': 'current',
    }
    res = testapp.post_json('/sequence_file_set', item, status=201)
    assert res.json['@graph'][0]['trimmed_cram'] == sequence_file_cram['@id']


def test_sequence_file_set_ultima_both_crams_success(testapp, other_lab, sequence_file_cram,
                                                     sequence_file_with_aliases,
                                                     droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'library': droplet_based_library['@id'],
        'run_cardinality': 'single-end',
        'untrimmed_cram': sequence_file_cram['@id'],
        'trimmed_cram': sequence_file_with_aliases['@id'],
        'sequencing_platform': 'Ultima Genomics UG 100',
        'status': 'current',
    }
    res = testapp.post_json('/sequence_file_set', item, status=201)
    assert res.json['@graph'][0]['untrimmed_cram'] == sequence_file_cram['@id']
    assert res.json['@graph'][0]['trimmed_cram'] == sequence_file_with_aliases['@id']


def test_sequence_file_set_mixed_fastq_and_cram_fails(testapp, other_lab, sequence_file,
                                                      sequence_file_cram, droplet_based_library):
    """FASTQ and CRAM files cannot be mixed in the same set."""
    testapp.post_json(
        '/sequence_file_set',
        {
            'lab': other_lab['@id'],
            'library': droplet_based_library['@id'],
            'run_cardinality': 'single-end',
            'read1': sequence_file['@id'],
            'untrimmed_cram': sequence_file_cram['@id'],
            'status': 'current',
        },
        status=422
    )


def test_sequence_file_set_cram_with_non_single_end_fails(testapp, other_lab, sequence_file_cram,
                                                          sequence_file, droplet_based_library):
    """CRAM files are only allowed with single-end cardinality."""
    testapp.post_json(
        '/sequence_file_set',
        {
            'lab': other_lab['@id'],
            'library': droplet_based_library['@id'],
            'run_cardinality': 'paired-end',
            'untrimmed_cram': sequence_file_cram['@id'],
            'read1': sequence_file['@id'],
            'status': 'current',
        },
        status=422
    )


def test_sequence_file_set_single_end_no_file_fails(testapp, other_lab, droplet_based_library):
    """Single-end requires at least read1 or a CRAM file."""
    testapp.post_json(
        '/sequence_file_set',
        {
            'lab': other_lab['@id'],
            'library': droplet_based_library['@id'],
            'run_cardinality': 'single-end',
            'status': 'current',
        },
        status=422
    )


def test_sequence_file_set_platform_enum(testapp, other_lab, sequence_file, droplet_based_library):
    testapp.post_json(
        '/sequence_file_set',
        {
            'lab': other_lab['@id'],
            'library': droplet_based_library['@id'],
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
        'Ultima Genomics UG 100',
    ]
)
def test_sequence_file_set_platform_enum_values(testapp, other_lab, sequence_file,
                                                sequence_file_cram, droplet_based_library,
                                                platform):
    if 'Ultima' in platform:
        item = {
            'lab': other_lab['@id'],
            'library': droplet_based_library['@id'],
            'run_cardinality': 'single-end',
            'untrimmed_cram': sequence_file_cram['@id'],
            'sequencing_platform': platform,
            'status': 'current',
        }
    else:
        item = {
            'lab': other_lab['@id'],
            'library': droplet_based_library['@id'],
            'run_cardinality': 'single-end',
            'read1': sequence_file['@id'],
            'sequencing_platform': platform,
            'status': 'current',
        }
    res = testapp.post_json('/sequence_file_set', item, status=201)
    assert res.json['@graph'][0]['sequencing_platform'] == platform


@pytest.mark.parametrize(
    'cro_order',
    [
        'AN00012345',
        'NVUS123456789-01',
    ]
)
def test_sequence_file_set_cro_order_valid(testapp, other_lab, sequence_file,
                                           droplet_based_library, cro_order):
    item = {
        'lab': other_lab['@id'],
        'library': droplet_based_library['@id'],
        'run_cardinality': 'single-end',
        'read1': sequence_file['@id'],
        'CRO_order': cro_order,
        'status': 'current',
    }
    res = testapp.post_json('/sequence_file_set', item, status=201)
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
def test_sequence_file_set_cro_order_invalid(testapp, other_lab, sequence_file,
                                             droplet_based_library, cro_order):
    testapp.post_json(
        '/sequence_file_set',
        {
            'lab': other_lab['@id'],
            'library': droplet_based_library['@id'],
            'run_cardinality': 'single-end',
            'read1': sequence_file['@id'],
            'CRO_order': cro_order,
            'status': 'current',
        },
        status=422
    )


def test_sequence_file_set_library_linkto_validation(testapp, other_lab, sequence_file):
    testapp.post_json(
        '/sequence_file_set',
        {
            'lab': other_lab['@id'],
            'library': '/invalid/library/path/',
            'run_cardinality': 'single-end',
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
def test_sequence_file_set_illumina_cardinality_values(testapp, other_lab, sequence_file,
                                                       sequence_file_with_description,
                                                       sequence_file_with_aliases,
                                                       sequence_file_cram,
                                                       droplet_based_library,
                                                       run_cardinality):
    item = {
        'lab': other_lab['@id'],
        'library': droplet_based_library['@id'],
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

    res = testapp.post_json('/sequence_file_set', item, status=201)
    assert res.json['@graph'][0]['run_cardinality'] == run_cardinality


def test_sequence_file_set_create_with_all_optional_fields(testapp, other_lab, sequence_file,
                                                           sequence_file_with_description,
                                                           droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'library': droplet_based_library['@id'],
        'run_cardinality': 'paired-end',
        'read1': sequence_file['@id'],
        'read2': sequence_file_with_description['@id'],
        'sequencing_platform': 'Illumina NextSeq 1000',
        'CRO_order': 'AN00012345',
        'description': 'Test sequence file set with all fields',
        'aliases': ['lattice:test-sfs-001'],
        'status': 'current',
    }
    res = testapp.post_json('/sequence_file_set', item, status=201)
    assert res.json['@graph'][0]['sequencing_platform'] == 'Illumina NextSeq 1000'
    assert res.json['@graph'][0]['CRO_order'] == 'AN00012345'
    assert res.json['@graph'][0]['description'] == 'Test sequence file set with all fields'
    assert 'lattice:test-sfs-001' in res.json['@graph'][0]['aliases']
