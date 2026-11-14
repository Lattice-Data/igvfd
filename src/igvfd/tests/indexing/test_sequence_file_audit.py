import pytest


pytestmark = [pytest.mark.indexing]


LIBRARY = '/droplet_based_libraries/d1e2f3a4-b5c6-7890-def1-234567890abc/'
LAB = '/labs/teri-klein/'
CATEGORY = 'multiple sequence file sets'


def _post_fastq(testapp, name):
    return testapp.post_json('/sequence_file', {
        'lab': LAB,
        'file_format': 'fastq',
        's3_uri': f's3://lattice-test-data/sequence/{name}',
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'read_count': 15_000_000,
        'status': 'current',
    }, status=201).json['@graph'][0]


def _post_set(testapp, read1):
    return testapp.post_json('/sequence_file_set', {
        'lab': LAB,
        'library': LIBRARY,
        'run_cardinality': 'single-end',
        'read1': read1['@id'],
        'status': 'current',
    }, status=201).json['@graph'][0]


def _flagged(testapp, f):
    res = testapp.get(
        f'/search/?type=SequenceFile&uuid={f["uuid"]}'
        f'&audit.ERROR.category={CATEGORY}&field=uuid',
        status=(200, 404),
    )
    return len(res.json['@graph']) == 1


def test_indexing_multiple_sequence_file_sets_audit_follows_sets(
    testapp, workbook, poll_until_indexing_is_done
):
    f = _post_fastq(testapp, 'IDX_MULTI_SET_R1_001.fastq.gz')
    other = _post_fastq(testapp, 'IDX_MULTI_SET_OTHER_R1_001.fastq.gz')
    _post_set(testapp, f)
    other_set = _post_set(testapp, other)
    poll_until_indexing_is_done(testapp)
    assert not _flagged(testapp, f)

    # a new set naming the already-indexed file must reindex it
    second = _post_set(testapp, f)
    poll_until_indexing_is_done(testapp)
    assert _flagged(testapp, f)

    # deleting that set must reindex the file and clear the audit
    testapp.patch_json(second['@id'], {'status': 'deleted'}, status=200)
    poll_until_indexing_is_done(testapp)
    assert not _flagged(testapp, f)

    # an existing set patched to name the file must reindex it too
    testapp.patch_json(other_set['@id'], {'read1': f['@id']}, status=200)
    poll_until_indexing_is_done(testapp)
    assert _flagged(testapp, f)
