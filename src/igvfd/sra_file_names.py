"""Names under which a SequenceFile's reads are submitted to SRA.

A port of the naming rule in Lattice-Data/lattice-tools bcp/fastq_chunker
(plan.py and portal.py at commit 70d0b62, PR #375). The chunker splits every
FASTQ of a sequence file set into the same number of record-aligned chunks
once any mate reaches the SRA 100 GB per-file limit; this module computes the
names it gives them. Keep the two in lockstep: a change to the constants or
rules there must land here too, with the shared test vectors.

Pure functions, no snovault imports, so the rule can be tested on its own.
"""
import math
import re

GB = 10**9
LIMIT_BYTES = 100 * GB  # SRA's per-file limit, decimal GB (plan.py LIMIT_BYTES)
TARGET_BYTES = 80 * GB  # chunker default --target-gb (plan.py TARGET_BYTES)
ROUND_TO = 1_000_000  # reads per chunk rounding (plan.py ROUND_TO); never changes a name
MIN_SUFFIX_WIDTH = 3
EXTENSIONS = ('.fastq.gz', '.fq.gz')
READ_SLOTS = ('read1', 'read2', 'read3', 'index1', 'index2')
_CHUNK_SHAPED = re.compile(r'(.+)\.part\d+')


def basename(s3_uri):
    return s3_uri.rsplit('/', 1)[-1]


def stem_of(filename):
    """The name without its FASTQ extension, or None for an extension the chunker rejects."""
    for ext in EXTENSIONS:
        if filename.endswith(ext) and len(filename) > len(ext):
            return filename[:-len(ext)]
    return None


def chunk_count(biggest_bytes, target_bytes=TARGET_BYTES, limit_bytes=LIMIT_BYTES):
    """A file below the limit is legal as-is and is never split."""
    if biggest_bytes < limit_bytes:
        return 1
    return math.ceil(biggest_bytes / target_bytes)


def suffix_width(n_chunks):
    return max(MIN_SUFFIX_WIDTH, len(str(n_chunks)))


def chunk_name(stem, index, width):
    return f'{stem}.part{index:0{width}d}.fastq.gz'


def reads_per_chunk(total_reads, n_chunks, round_to=ROUND_TO):
    """Reads in every chunk but the last; None where the chunker raises PlanError."""
    if n_chunks == 1:
        return total_reads
    if n_chunks > total_reads:
        return None
    exact = math.ceil(total_reads / n_chunks)
    rounded = math.ceil(exact / round_to) * round_to
    n = rounded if (n_chunks - 1) * rounded < total_reads else exact
    fits = (n_chunks - 1) * n < total_reads <= n_chunks * n
    if not fits or math.ceil(total_reads / n) != n_chunks:
        return None
    return n


def set_file_names(mates, target_bytes=TARGET_BYTES, limit_bytes=LIMIT_BYTES, round_to=ROUND_TO):
    """SRA file names for every read slot of one sequence file set.

    ``mates`` maps a read slot to that file's properties (``file_format``,
    ``s3_uri``, ``file_size``, ``read_count``). Returns ``{slot: [names]}``:
    the file's own basename when the set needs no splitting, else its chunk
    names. Returns None wherever ``fastq_chunker plan`` would refuse the set,
    so no name is ever advertised that the chunker will not produce.
    """
    if not mates or target_bytes >= limit_bytes:
        return None
    files = []
    for slot in READ_SLOTS:
        if slot not in mates:
            continue
        props = mates[slot]
        if props.get('file_format') != 'fastq':
            return None
        if not all(props.get(key) for key in ('s3_uri', 'file_size', 'read_count')):
            return None
        name = basename(props['s3_uri'])
        stem = stem_of(name)
        if stem is None:
            return None
        files.append((slot, name, stem, int(props['file_size']), int(props['read_count'])))
    if not files:
        return None
    # every chunk of a plan lands under one prefix, so stems must be distinct, and
    # no stem may look like another's chunk (plan.make_plan)
    stems = [stem for _, _, stem, _, _ in files]
    if len(set(stems)) != len(stems):
        return None
    for stem in stems:
        m = _CHUNK_SHAPED.fullmatch(stem)
        if m and m.group(1) in stems:
            return None
    # mates must hold identical read counts (plan.plan_group)
    counts = {reads for *_, reads in files}
    if len(counts) != 1:
        return None
    total_reads = counts.pop()
    if total_reads <= 0:
        return None
    biggest = max(size for _, _, _, size, _ in files)
    n_chunks = chunk_count(biggest, target_bytes, limit_bytes)
    n = reads_per_chunk(total_reads, n_chunks, round_to)
    if n is None:
        return None
    if n_chunks > 1 and biggest * n / total_reads >= limit_bytes:
        return None
    if n_chunks == 1:
        return {slot: [name] for slot, name, _, _, _ in files}
    width = suffix_width(n_chunks)
    return {
        slot: [chunk_name(stem, k, width) for k in range(1, n_chunks + 1)]
        for slot, _, stem, _, _ in files
    }
