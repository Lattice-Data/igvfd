import pytest


pytestmark = [pytest.mark.indexing]


GB = 10**9
LIBRARY = '/droplet_based_libraries/d1e2f3a4-b5c6-7890-def1-234567890abc/'
LAB = '/labs/teri-klein/'


def _post_fastq(testapp, name, file_size):
    return testapp.post_json('/sequence_file', {
        'lab': LAB,
        'file_format': 'fastq',
        's3_uri': f's3://lattice-test-data/sequence/{name}',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'read_count': 2_000_000_000,
        'file_size': file_size,
        'status': 'current',
    }, status=201).json['@graph'][0]


def _post_set(testapp, read1, read2):
    return testapp.post_json('/sequence_file_set', {
        'lab': LAB,
        'library': LIBRARY,
        'run_cardinality': 'paired-end',
        'read1': read1['@id'],
        'read2': read2['@id'],
        'status': 'current',
    }, status=201).json['@graph'][0]


def _indexed_names(testapp, f):
    res = testapp.get(f'/search/?type=SequenceFile&uuid={f["uuid"]}&field=sra_file_names')
    [hit] = res.json['@graph']
    return hit.get('sra_file_names')


def test_indexing_sra_file_names_follow_mates(testapp, workbook, poll_until_indexing_is_done):
    r1 = _post_fastq(testapp, 'IDX_SRA_R1_001.fastq.gz', 45 * GB)
    r2 = _post_fastq(testapp, 'IDX_SRA_R2_001.fastq.gz', 50 * GB)
    _post_set(testapp, r1, r2)
    poll_until_indexing_is_done(testapp)
    assert _indexed_names(testapp, r1) == ['IDX_SRA_R1_001.fastq.gz']

    # a mate's file_size crossing the limit must reindex this file
    testapp.patch_json(r2['@id'], {'file_size': 160 * GB + 1}, status=200)
    poll_until_indexing_is_done(testapp)
    assert _indexed_names(testapp, r1) == [
        f'IDX_SRA_R1_001.part{k:03d}.fastq.gz' for k in range(1, 4)
    ]

    # a new set naming the mate (not r1 itself) must also reindex r1
    other_r1 = _post_fastq(testapp, 'IDX_SRA_OTHER_R1_001.fastq.gz', 45 * GB)
    _post_set(testapp, other_r1, r2)
    poll_until_indexing_is_done(testapp)
    assert _indexed_names(testapp, r1) is None
