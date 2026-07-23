import pytest

from pyramid.exceptions import HTTPBadRequest


def test_iter_matrix_file_set_files_flattens_both_link_lists():
    from igvfd.metadata.metadata import iter_matrix_file_set_files
    raw = {'@id': '/raw_matrix_files/a/', 'file_format': 'h5'}
    processed = {'@id': '/processed_matrix_files/b/', 'file_format': 'h5ad'}
    file_set = {
        'raw_matrix_files': [raw],
        'processed_matrix_files': [processed],
    }
    assert iter_matrix_file_set_files(file_set) == [raw, processed]


def test_iter_matrix_file_set_files_skips_absent_and_empty():
    from igvfd.metadata.metadata import iter_matrix_file_set_files
    raw = {'@id': '/raw_matrix_files/a/', 'file_format': 'h5'}
    assert iter_matrix_file_set_files({'raw_matrix_files': [raw]}) == [raw]
    assert iter_matrix_file_set_files({'raw_matrix_files': []}) == []
    assert iter_matrix_file_set_files({'processed_matrix_files': None}) == []
    assert iter_matrix_file_set_files({}) == []


def test_iter_matrix_file_set_files_accepts_single_non_list_value():
    from igvfd.metadata.metadata import iter_matrix_file_set_files
    raw = {'@id': '/raw_matrix_files/a/', 'file_format': 'h5'}
    assert iter_matrix_file_set_files({'raw_matrix_files': raw}) == [raw]


def test_metadata_report_splits_file_and_file_set_columns(dummy_request):
    from igvfd.metadata.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = 'type=MatrixFileSet'
    report = MetadataReport(dummy_request)
    report._initialize_report()
    assert list(report.file_column_to_fields_mapping) == [
        'File ID',
        'File aliases',
        'File format',
    ]
    assert report.file_column_to_fields_mapping['File ID'] == ['@id']
    assert report.file_column_to_fields_mapping['File format'] == ['file_format']
    assert 'File set ID' in report.experiment_column_to_fields_mapping
    assert report.experiment_column_to_fields_mapping['File set type'] == ['@type']


def test_metadata_report_header_order_and_audit_columns(dummy_request):
    from igvfd.metadata.constants import FROM_MATRIX_FILE_SET_FIELDS
    from igvfd.metadata.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = 'type=MatrixFileSet'
    report = MetadataReport(dummy_request)
    report._build_header()
    assert report.header[:len(FROM_MATRIX_FILE_SET_FIELDS)] == list(FROM_MATRIX_FILE_SET_FIELDS)
    assert report.header[-3:] == [
        'Audit WARNING',
        'Audit NOT_COMPLIANT',
        'Audit ERROR',
    ]


def test_metadata_report_type_cell_includes_concrete_type(dummy_request):
    from igvfd.metadata.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = 'type=MatrixFileSet'
    report = MetadataReport(dummy_request)
    report._initialize_report()
    experiment_data = report._get_experiment_data({
        '@id': '/matrix-file-sets/abc/',
        '@type': ['MatrixFileSet', 'FileSet', 'Item'],
        'status': 'current',
    })
    assert experiment_data['File set type'] == 'FileSet, Item, MatrixFileSet'


def test_make_experiment_cell_type_order_is_deterministic():
    from igvfd.metadata.serializers import make_experiment_cell
    experiment = {
        '@type': ['MatrixFileSet', 'FileSet', 'Item'],
    }
    assert make_experiment_cell(['@type'], experiment) == 'FileSet, Item, MatrixFileSet'


def test_get_audit_data_category_order_is_deterministic(dummy_request):
    from igvfd.metadata.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = 'type=MatrixFileSet'
    report = MetadataReport(dummy_request)
    report._initialize_report()
    audit_data = report._get_audit_data(
        {
            'WARNING': ['zebra audit', 'alpha audit'],
        },
        {
            'WARNING': ['middle audit'],
        },
    )
    assert audit_data['Audit WARNING'] == 'alpha audit, middle audit, zebra audit'


def test_metadata_report_parses_file_inequality_filters(dummy_request):
    from igvfd.metadata.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=MatrixFileSet&raw_matrix_files.observation_count=gte:12000'
    )
    report = MetadataReport(dummy_request)
    report._initialize_report()
    assert list(report.positive_file_inequalities_by_link['raw_matrix_files']) == [
        'observation_count',
    ]
    assert not report._should_not_report_file(
        {'observation_count': 12000},
        'raw_matrix_files',
    )
    assert report._should_not_report_file(
        {'observation_count': 11500},
        'raw_matrix_files',
    )
    # A filter on raw_matrix_files scopes output to that array, so files in the
    # unfiltered processed_matrix_files array are excluded entirely.
    assert report._should_not_report_file(
        {'observation_count': 11500},
        'processed_matrix_files',
    )


def test_metadata_report_drops_file_inequality_params_from_search_query(dummy_request):
    from igvfd.metadata.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=MatrixFileSet&raw_matrix_files.observation_count=gte:12000'
    )
    report = MetadataReport(dummy_request)
    report._initialize_report()
    report._build_params()
    report._build_query_string()
    params = report.query_string.params_to_list()
    assert ('raw_matrix_files.observation_count', 'gte:12000') not in params
    assert report.positive_file_inequalities_by_link['raw_matrix_files']['observation_count']


def test_metadata_report_output_sorted_row_matches_header(dummy_request):
    from igvfd.metadata.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = 'type=MatrixFileSet'
    report = MetadataReport(dummy_request)
    report._initialize_report()
    experiment_data = {
        column: f'exp-{column}'
        for column in report.experiment_column_to_fields_mapping
    }
    file_data = {
        column: f'file-{column}'
        for column in report.file_column_to_fields_mapping
    }
    file_data.update({
        'Audit WARNING': 'warn',
        'Audit NOT_COMPLIANT': '',
        'Audit ERROR': '',
    })
    row = report._output_sorted_row(experiment_data, file_data)
    assert len(row) == len(report.header)
    for column, value in zip(report.header, row):
        if column.startswith('Audit'):
            assert value == file_data[column]
        elif column in file_data and not column.startswith('Audit'):
            assert value == f'file-{column}'
        else:
            assert value == f'exp-{column}'


def test_metadata_report_rejects_legacy_files_filters(dummy_request):
    from igvfd.metadata.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=MatrixFileSet&files.file_format=h5ad'
    )
    report = MetadataReport(dummy_request)
    with pytest.raises(HTTPBadRequest):
        report._initialize_report()


def test_metadata_report_rejects_negated_file_format_filter(dummy_request):
    from igvfd.metadata.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=MatrixFileSet&processed_matrix_files.file_format!=h5ad'
    )
    report = MetadataReport(dummy_request)
    with pytest.raises(HTTPBadRequest):
        report._initialize_report()


def test_metadata_report_rejects_not_exists_file_filter(dummy_request):
    from igvfd.metadata.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=MatrixFileSet&raw_matrix_files.file_format!=*'
    )
    report = MetadataReport(dummy_request)
    with pytest.raises(HTTPBadRequest):
        report._initialize_report()


def test_metadata_report_rejects_negated_inequality_file_filter(dummy_request):
    from igvfd.metadata.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=MatrixFileSet&raw_matrix_files.observation_count!=gte:12000'
    )
    report = MetadataReport(dummy_request)
    with pytest.raises(HTTPBadRequest):
        report._initialize_report()


def test_metadata_report_allows_positive_file_format_filter(dummy_request):
    from igvfd.metadata.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=MatrixFileSet&processed_matrix_files.file_format=h5ad'
    )
    report = MetadataReport(dummy_request)
    report._initialize_report()
    assert report.positive_file_param_set_by_link['processed_matrix_files'] == {
        'file_format': {'h5ad'},
    }


def test_metadata_report_should_not_report_file_param_filter(dummy_request):
    from igvfd.metadata.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=MatrixFileSet&raw_matrix_files.file_format=h5'
    )
    report = MetadataReport(dummy_request)
    report._initialize_report()
    assert not report._should_not_report_file({'file_format': 'h5'}, 'raw_matrix_files')
    assert report._should_not_report_file({'file_format': 'h5ad'}, 'raw_matrix_files')
    # Only raw_matrix_files is filtered, so processed_matrix_files files are excluded.
    assert report._should_not_report_file({'file_format': 'h5ad'}, 'processed_matrix_files')


def test_matrix_file_set_metadata_allowed_types_decorator():
    from igvfd.metadata.decorators import allowed_types
    from igvfd.metadata.constants import MATRIX_FILE_SET_METADATA_ALLOWED_TYPES

    @allowed_types(MATRIX_FILE_SET_METADATA_ALLOWED_TYPES)
    def endpoint(context, request):
        return True

    class Request:
        def __init__(self, params):
            self.params = params

    context = {}
    with pytest.raises(HTTPBadRequest):
        endpoint(context, Request({}))
    with pytest.raises(HTTPBadRequest):
        endpoint(context, Request({'type': 'SequenceFileSet'}))
    assert endpoint(context, Request({'type': 'MatrixFileSet'}))


def test_group_audits_by_files_and_type_uses_lattice_paths():
    from igvfd.metadata.metadata import group_audits_by_files_and_type
    audits = {
        'WARNING': [
            {
                'category': 'missing software version',
                'path': '/raw_matrix_files/abc/',
            },
            {
                'category': 'something else',
                'path': '/matrix_file_sets/xyz/',
            },
        ],
        'ERROR': [
            {
                'category': 'bad thing',
                'path': '/processed_matrix_files/def/',
            },
        ],
    }
    file_audits, other_audits = group_audits_by_files_and_type(audits)
    assert file_audits['/raw_matrix_files/abc/']['WARNING'] == ['missing software version']
    assert file_audits['/processed_matrix_files/def/']['ERROR'] == ['bad thing']
    assert other_audits['WARNING'] == ['something else']


def test_metadata_report_drops_file_link_filter_params_from_search_query(dummy_request):
    from igvfd.metadata.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=MatrixFileSet&processed_matrix_files.file_format=h5ad'
    )
    report = MetadataReport(dummy_request)
    report._initialize_report()
    report._build_params()
    report._build_query_string()
    params = report.query_string.params_to_list()
    assert ('processed_matrix_files.file_format', 'h5ad') not in params
    assert report.positive_file_param_set_by_link['processed_matrix_files'] == {
        'file_format': {'h5ad'},
    }
