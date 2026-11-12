import pytest

from igvfd.audit.matrix_file_set import audit_matrix_file_set_duplicate_geo_file_name


CATEGORY = 'duplicate GEO file name'
SET_ID = '/matrix-file-sets/c3b2a1f0-0000-4000-8000-000000000001/'


def _cellranger_uri(group, sample, run='Run_2026_01_01'):
    return (
        f's3://lattice-test-data/test-project/AN00000001/{group}/processed/cellranger/{run}/'
        f'outs/per_sample_outs/{sample}/count/sample_filtered_feature_bc_matrix.h5'
    )


class _StubRequest:
    def __init__(self, files):
        self.files = files

    def embed(self, path, frame):
        assert frame == '@@object?skip_calculated=true'
        return self.files[path]


def _audit(files):
    """files: {file_id: stored properties}, linked in that order."""
    value = {
        '@type': ['MatrixFileSet'],
        '@id': SET_ID,
        'raw_matrix_files': list(files),
    }
    return list(audit_matrix_file_set_duplicate_geo_file_name(value, {'request': _StubRequest(files)}))


def _file_id(n):
    return f'/raw-matrix-files/IGVFDTEST{n:04d}/'


def test_distinct_geo_file_names_no_audit():
    assert _audit({
        _file_id(1): {'s3_uri': _cellranger_uri('G1', 'S1'), 'status': 'current'},
        _file_id(2): {'s3_uri': _cellranger_uri('G1', 'S2'), 'status': 'current'},
        _file_id(3): {'s3_uri': _cellranger_uri('G2', 'S1'), 'status': 'current'},
    }) == []


def test_no_raw_matrix_files_no_audit():
    value = {'@type': ['MatrixFileSet'], '@id': SET_ID}
    assert list(audit_matrix_file_set_duplicate_geo_file_name(value, {'request': _StubRequest({})})) == []


@pytest.mark.parametrize('first, second, name', [
    # the same GroupID run through Cell Ranger twice
    (
        _cellranger_uri('G1', 'S1', run='Run_2026_01_01'),
        _cellranger_uri('G1', 'S1', run='Run_2026_03_01'),
        'G1_S1_sample_filtered_feature_bc_matrix.h5',
    ),
    # "_" inside a GroupID and inside a sample give the same joined name
    (
        _cellranger_uri('A_B', 'C'),
        _cellranger_uri('A', 'B_C'),
        'A_B_C_sample_filtered_feature_bc_matrix.h5',
    ),
])
def test_duplicate_geo_file_name_audit(first, second, name):
    failures = _audit({
        _file_id(1): {'s3_uri': first, 'status': 'current'},
        _file_id(2): {'s3_uri': second, 'status': 'current'},
    })
    assert len(failures) == 1
    assert failures[0].category == CATEGORY
    assert failures[0].__json__()['level_name'] == 'ERROR'
    assert f'share `geo_file_name` `{name}`' in failures[0].detail
    assert 'IGVFDTEST0001' in failures[0].detail
    assert 'IGVFDTEST0002' in failures[0].detail


def test_one_failure_per_duplicated_name():
    failures = _audit({
        _file_id(1): {'s3_uri': _cellranger_uri('G1', 'S1', run='Run_1'), 'status': 'current'},
        _file_id(2): {'s3_uri': _cellranger_uri('G1', 'S1', run='Run_2'), 'status': 'current'},
        _file_id(3): {'s3_uri': _cellranger_uri('G2', 'S2', run='Run_1'), 'status': 'current'},
        _file_id(4): {'s3_uri': _cellranger_uri('G2', 'S2', run='Run_2'), 'status': 'current'},
        _file_id(5): {'s3_uri': _cellranger_uri('G3', 'S3'), 'status': 'current'},
    })
    assert len(failures) == 2
    assert '`G1_S1_sample_filtered_feature_bc_matrix.h5`' in failures[0].detail
    assert '`G2_S2_sample_filtered_feature_bc_matrix.h5`' in failures[1].detail


def test_deleted_file_does_not_count():
    assert _audit({
        _file_id(1): {'s3_uri': _cellranger_uri('G1', 'S1', run='Run_1'), 'status': 'deleted'},
        _file_id(2): {'s3_uri': _cellranger_uri('G1', 'S1', run='Run_2'), 'status': 'current'},
    }) == []


def test_files_without_geo_file_name_not_compared():
    # outside the Cell Ranger layout there is no geo_file_name, even for equal basenames
    assert _audit({
        _file_id(1): {'s3_uri': 's3://bucket-a/matrix/raw.h5', 'status': 'current'},
        _file_id(2): {'s3_uri': 's3://bucket-b/matrix/raw.h5', 'status': 'current'},
        _file_id(3): {'no_file_available': True, 'status': 'current'},
        _file_id(4): {'no_file_available': True, 'status': 'current'},
    }) == []


def _post_raw_matrix_file(testapp, other_lab, tissue, s3_uri):
    item = {
        'lab': other_lab['@id'],
        'file_format': 'h5',
        's3_uri': s3_uri,
        'crc64nvme_base64': 'AAAAAAAAAAA',
        'samples': [tissue['@id']],
        'software': 'Cell Ranger',
        'software_version': '7.1.0',
        'genome_assembly': 'GRCh38',
        'is_multiplexed': False,
        'status': 'current',
    }
    return testapp.post_json('/raw_matrix_file', item, status=201).json['@graph'][0]


def _categories(res):
    return [error['category'] for errors in res.json['audit'].values() for error in errors]


def test_duplicate_geo_file_name_audit_integration(testapp, indexer_testapp, other_lab, tissue):
    first = _post_raw_matrix_file(testapp, other_lab, tissue, _cellranger_uri('G1', 'S1', run='Run_1'))
    second = _post_raw_matrix_file(testapp, other_lab, tissue, _cellranger_uri('G1', 'S1', run='Run_2'))
    matrix_file_set = testapp.post_json(
        '/matrix_file_set',
        {
            'lab': other_lab['@id'],
            'raw_matrix_files': [first['@id'], second['@id']],
            'status': 'current',
        },
        status=201,
    ).json['@graph'][0]
    res = indexer_testapp.get(matrix_file_set['@id'] + '@@index-data')
    assert any(
        error['category'] == CATEGORY
        for error in res.json['audit'].get('ERROR', [])
    )
    # retiring the superseded run clears the audit
    testapp.patch_json(first['@id'], {'status': 'deleted'}, status=200)
    res = indexer_testapp.get(matrix_file_set['@id'] + '@@index-data')
    assert CATEGORY not in _categories(res)


def test_matrix_file_set_without_cellranger_files_no_audit(indexer_testapp, matrix_file_set):
    res = indexer_testapp.get(matrix_file_set['@id'] + '@@index-data')
    assert CATEGORY not in _categories(res)
