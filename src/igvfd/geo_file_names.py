"""Name under which a RawMatrixFile is submitted to GEO.

Cell Ranger gives its outputs the same names in every run
(``filtered_feature_bc_matrix.h5``, ``sample_filtered_feature_bc_matrix.h5``),
so GEO needs a name made unique by where the file sits on S3:

    s3://<bucket>/.../<GroupID>/processed/cellranger/<run>/outs/<basename>
    s3://<bucket>/.../<GroupID>/processed/cellranger/<run>/outs/per_sample_outs/<sample>/[count/]<basename>

The name is ``<GroupID>_<sample>_<basename>``, or ``<GroupID>_<basename>``
when there is no per-sample folder or the sample folder repeats the GroupID
(a non-multiplexed experiment run through ``cellranger multi``). The ``_``
matches the separator inside Cell Ranger's own names.

Only a path with a ``processed/cellranger`` folder is taken to be Cell Ranger,
and so 10x, output. Any other path gets no name: plate assays already have
distinct file names.

Pure functions, no snovault imports, so the rule can be tested on its own.
"""
SCHEME = 's3://'
SEPARATOR = '_'
CELLRANGER_FOLDERS = ('processed', 'cellranger')
PER_SAMPLE_FOLDER = 'per_sample_outs'


def geo_name_from_s3_uri(s3_uri):
    """The GEO name for a Cell Ranger output path, or None for any other path."""
    if not s3_uri.startswith(SCHEME):
        return None
    # segments[0] is the bucket
    segments = s3_uri[len(SCHEME):].split('/')
    # The GroupID folder sits right before processed/cellranger, so it can be no
    # earlier than segments[1], and the basename must come after both folders.
    for i in range(2, len(segments) - 2):
        if tuple(segments[i:i + 2]) == CELLRANGER_FOLDERS:
            break
    else:
        return None
    group = segments[i - 1]
    basename = segments[-1]
    sample = None
    # the sample folder is never the basename itself
    for j in range(i + 2, len(segments) - 2):
        if segments[j] == PER_SAMPLE_FOLDER:
            sample = segments[j + 1]
            break
    if not group or not basename or sample == '':
        return None
    parts = [group]
    if sample is not None and sample != group:
        parts.append(sample)
    parts.append(basename)
    return SEPARATOR.join(parts)
