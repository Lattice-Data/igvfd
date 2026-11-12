"""GEO file names, pinned to the S3 layouts of production RawMatrixFiles.

The first four vectors are real production paths, one per layout Cell Ranger
output takes on S3 today.
"""
import pytest

from igvfd.geo_file_names import geo_name_from_s3_uri


@pytest.mark.parametrize('s3_uri, expected', [
    # cellranger multi, per-sample output under count/ (Psomagen)
    (
        's3://czi-psomagen/weissman-scaling-in-vivo-perturb-seq-in-the-liver-and-beyond/AN00027039/'
        'Refed_14/processed/cellranger/Run_2025_12_16/outs/per_sample_outs/13_A1/count/'
        'sample_filtered_feature_bc_matrix.h5',
        'Refed_14_13_A1_sample_filtered_feature_bc_matrix.h5',
    ),
    # per-sample output without count/ (Novogene)
    (
        's3://czi-novogene/ny-biohub-califano/NVUS2024101701-07/AZ116E_AZ116LF/processed/cellranger/'
        'Run_2025-12-03_biohub/outs/per_sample_outs/THP-1_marcophages_TFcoTF_A/'
        'sample_filtered_feature_bc_matrix.h5',
        'AZ116E_AZ116LF_THP-1_marcophages_TFcoTF_A_sample_filtered_feature_bc_matrix.h5',
    ),
    # no per-sample folder: the GroupID alone
    (
        's3://czi-psomagen/thiagarajah-gut-age-sequencing/AN00028448/CZI25110403/processed/cellranger/'
        'Run_2026_08_06/outs/filtered_feature_bc_matrix.h5',
        'CZI25110403_filtered_feature_bc_matrix.h5',
    ),
    # non-multiplexed run through cellranger multi: the sample repeats the GroupID, used once
    (
        's3://czi-psomagen/platt-causal-understanding-biological-systems-with-in-vivo-genotype-phenotype-maps/'
        'AN00026453/ES_m3_5Pv3/processed/cellranger/Run_2025_11_07/outs/per_sample_outs/ES_m3_5Pv3/count/'
        'sample_filtered_feature_bc_matrix.h5',
        'ES_m3_5Pv3_sample_filtered_feature_bc_matrix.h5',
    ),
    # only the processed/cellranger folder is required, wherever it sits
    ('s3://bucket/G1/processed/cellranger/matrix.h5', 'G1_matrix.h5'),
    ('s3://bucket/a/b/c/d/G1/processed/cellranger/run/outs/matrix.h5', 'G1_matrix.h5'),
    # a per_sample_outs folder with nothing between it and the file names no sample
    ('s3://bucket/G1/processed/cellranger/run/outs/per_sample_outs/matrix.h5', 'G1_matrix.h5'),
])
def test_geo_name_from_cellranger_path(s3_uri, expected):
    assert geo_name_from_s3_uri(s3_uri) == expected


def test_geo_name_ignores_bucket_project_order_and_run():
    a = 's3://bucket-a/project-a/AN1/G1/processed/cellranger/Run_1/outs/per_sample_outs/S1/count/m.h5'
    b = 's3://bucket-b/project-b/AN2/G1/processed/cellranger/Run_2/outs/per_sample_outs/S1/count/m.h5'
    assert geo_name_from_s3_uri(a) == geo_name_from_s3_uri(b) == 'G1_S1_m.h5'


@pytest.mark.parametrize('s3_uri', [
    # not Cell Ranger output
    's3://lattice-test-data/matrix/raw-001.h5',
    's3://bucket/G1/processed/parse/run/outs/matrix.h5',
    's3://bucket/G1/cellranger/processed/matrix.h5',
    # folder names are matched whole
    's3://bucket/G1/unprocessed/cellranger/matrix.h5',
    's3://bucket/G1/processed/cellranger-arc/run/outs/matrix.h5',
    # no GroupID folder: processed/cellranger sits right under the bucket
    's3://bucket/processed/cellranger/run/outs/matrix.h5',
    # no file after the Cell Ranger folders
    's3://bucket/G1/processed/cellranger',
    's3://bucket/G1/processed/cellranger/run/outs/',
    # empty folders where the GroupID or sample would be
    's3://bucket//processed/cellranger/run/outs/matrix.h5',
    's3://bucket/G1/processed/cellranger/run/outs/per_sample_outs//count/matrix.h5',
    # not an S3 URI
    'https://bucket/G1/processed/cellranger/run/outs/matrix.h5',
])
def test_geo_name_absent_outside_cellranger_layout(s3_uri):
    assert geo_name_from_s3_uri(s3_uri) is None
