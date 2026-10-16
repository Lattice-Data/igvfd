"""SRA file names, pinned to vectors produced by lattice-tools fastq_chunker at 70d0b62.

V1 is the chunker's own worked example (test_plan_group_worked_example in
lattice-tools), so both suites assert the same case.
"""
import pytest

from igvfd.sra_file_names import (
    GB,
    chunk_count,
    set_file_names,
    stem_of,
    suffix_width,
)


def _fastq(name, size, reads):
    return {
        'file_format': 'fastq',
        's3_uri': f's3://lattice-test-data/sequence/{name}',
        'file_size': size,
        'read_count': reads,
    }


def _parts(stem, n, width=3):
    return [f'{stem}.part{k:0{width}d}.fastq.gz' for k in range(1, n + 1)]


def test_v1_worked_example_510_gb_r2_gives_seven_parts_for_every_mate():
    reads = 2_000_000_000
    mates = {
        'index1': _fastq('LIB01_S1_L001_I1_001.fastq.gz', 31 * GB, reads),
        'index2': _fastq('LIB01_S1_L001_I2_001.fastq.gz', 29 * GB, reads),
        'read1': _fastq('LIB01_S1_L001_R1_001.fastq.gz', 480 * GB, reads),
        'read2': _fastq('LIB01_S1_L001_R2_001.fastq.gz', 510 * GB, reads),
    }
    assert set_file_names(mates) == {
        'index1': _parts('LIB01_S1_L001_I1_001', 7),
        'index2': _parts('LIB01_S1_L001_I2_001', 7),
        'read1': _parts('LIB01_S1_L001_R1_001', 7),
        'read2': _parts('LIB01_S1_L001_R2_001', 7),
    }


def test_v2_one_byte_under_limit_keeps_basenames():
    mates = {
        'read1': _fastq('S2_R1_001.fastq.gz', 40 * GB, 900_000_000),
        'read2': _fastq('S2_R2_001.fastq.gz', 99_999_999_999, 900_000_000),
    }
    assert set_file_names(mates) == {
        'read1': ['S2_R1_001.fastq.gz'],
        'read2': ['S2_R2_001.fastq.gz'],
    }


def test_v3_exactly_at_limit_is_split():
    mates = {
        'read1': _fastq('S3_R1_001.fastq.gz', 30 * GB, 900_000_000),
        'read2': _fastq('S3_R2_001.fastq.gz', 100_000_000_000, 900_000_000),
    }
    assert set_file_names(mates) == {
        'read1': _parts('S3_R1_001', 2),
        'read2': _parts('S3_R2_001', 2),
    }


def test_v4_index_reads_get_same_count_as_biggest_mate():
    reads = 2_000_000_000
    mates = {
        'read1': _fastq('S4_R1_001.fastq.gz', 45 * GB, reads),
        'read2': _fastq('S4_R2_001.fastq.gz', 160 * GB, reads),
        'index1': _fastq('S4_I1_001.fastq.gz', 6 * GB, reads),
        'index2': _fastq('S4_I2_001.fastq.gz', 6 * GB, reads),
    }
    assert set_file_names(mates) == {
        slot: _parts(f'S4_{tag}_001', 2)
        for slot, tag in (('read1', 'R1'), ('read2', 'R2'), ('index1', 'I1'), ('index2', 'I2'))
    }


def test_v5_one_byte_over_two_targets_gives_three_parts():
    mates = {
        'read1': _fastq('S5_R1_001.fastq.gz', 45 * GB, 2_000_000_000),
        'read2': _fastq('S5_R2_001.fastq.gz', 160 * GB + 1, 2_000_000_000),
    }
    assert set_file_names(mates) == {
        'read1': _parts('S5_R1_001', 3),
        'read2': _parts('S5_R2_001', 3),
    }


def test_v6_triplet_read3_shares_n():
    reads = 1_500_000_000
    mates = {
        'read1': _fastq('S6_R1_001.fastq.gz', 150 * GB, reads),
        'read2': _fastq('S6_R2_001.fastq.gz', 12 * GB, reads),
        'read3': _fastq('S6_R3_001.fastq.gz', 151 * GB, reads),
    }
    assert set_file_names(mates) == {
        'read1': _parts('S6_R1_001', 2),
        'read2': _parts('S6_R2_001', 2),
        'read3': _parts('S6_R3_001', 2),
    }


def test_v7_fq_gz_source_keeps_inner_dots_and_chunks_end_in_fastq_gz():
    mates = {'read1': _fastq('run.v2.S7_R1.fq.gz', 120 * GB, 800_000_000)}
    assert set_file_names(mates) == {
        'read1': ['run.v2.S7_R1.part001.fastq.gz', 'run.v2.S7_R1.part002.fastq.gz'],
    }


def test_unsplit_fq_gz_keeps_its_own_name():
    mates = {'read1': _fastq('run.v2.S7_R1.fq.gz', 20 * GB, 800_000_000)}
    assert set_file_names(mates) == {'read1': ['run.v2.S7_R1.fq.gz']}


def test_v8_target_decides_count():
    mates = {'read1': _fastq('S8_R1_001.fastq.gz', 170 * GB, 1_000_000_000)}
    assert set_file_names(mates) == {'read1': _parts('S8_R1_001', 3)}
    assert set_file_names(mates, target_bytes=90 * GB) == {'read1': _parts('S8_R1_001', 2)}


@pytest.mark.parametrize(
    'size, n_chunks, width',
    [
        (79_920 * GB, 999, 3),
        (80_000 * GB, 1000, 4),
    ],
)
def test_v9_suffix_width_grows_at_1000_chunks(size, n_chunks, width):
    mates = {'read1': _fastq('S9_R1_001.fastq.gz', size, 10_000_000_000)}
    names = set_file_names(mates)['read1']
    assert names == _parts('S9_R1_001', n_chunks, width)


def test_chunk_count_and_width_boundaries():
    assert chunk_count(100 * GB - 1) == 1
    assert chunk_count(100 * GB) == 2
    assert chunk_count(160 * GB) == 2
    assert chunk_count(160 * GB + 1) == 3
    assert suffix_width(1) == 3
    assert suffix_width(999) == 3
    assert suffix_width(1000) == 4


@pytest.mark.parametrize(
    'filename, stem',
    [
        ('A_R1.fastq.gz', 'A_R1'),
        ('run.v2.S7_R1.fq.gz', 'run.v2.S7_R1'),
        ('A_R1.fastq', None),
        ('A_R1.FASTQ.GZ', None),
        ('.fastq.gz', None),
        ('A_R1.bam', None),
    ],
)
def test_stem_of(filename, stem):
    assert stem_of(filename) == stem


BIG = 120 * GB
READS = 1_000_000_000


@pytest.mark.parametrize(
    'mates',
    [
        pytest.param({
            'read1': _fastq('R1_R1.fastq.gz', BIG, READS),
            'read2': _fastq('R1_R2.fastq.gz', BIG, READS + 1),
        }, id='R1-read-counts-differ'),
        pytest.param({'read1': _fastq('R2_R1.fastq.gz', 150 * GB, 3)}, id='R2-estimated-chunk-at-limit'),
        pytest.param({'read1': _fastq('R3_R1.fastq.gz', 200 * GB, 2)}, id='R3-too-few-reads'),
        pytest.param({
            'read1': {**_fastq('P3_R1.cram', BIG, READS), 'file_format': 'cram'},
        }, id='P3-cram'),
        pytest.param({
            'read1': _fastq('P4_R1.fastq.gz', BIG, 0),
            'read2': {k: v for k, v in _fastq('P4_R2.fastq.gz', BIG, READS).items() if k != 'file_size'},
        }, id='P4-missing-fields'),
        pytest.param({'read1': _fastq('P7_R1_001.fastq', BIG, READS)}, id='P7-uncompressed'),
        pytest.param({'read1': _fastq('P8_R1_001.FASTQ.GZ', BIG, READS)}, id='P8-uppercase-extension'),
        pytest.param({
            'read1': _fastq('M1.fastq.gz', 10 * GB, READS),
            'read2': {**_fastq('M1.fastq.gz', 10 * GB, READS), 's3_uri': 's3://other-bucket/M1.fastq.gz'},
        }, id='M1-shared-stem-even-unsplit'),
        pytest.param({
            'read1': _fastq('M2.fastq.gz', BIG, READS),
            'read2': _fastq('M2.part002.fastq.gz', BIG, READS),
        }, id='M2-chunk-shaped-stem'),
        pytest.param({}, id='no-read-slots'),
    ],
)
def test_refused_sets_get_no_names(mates):
    assert set_file_names(mates) is None
