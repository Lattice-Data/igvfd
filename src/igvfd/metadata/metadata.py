from collections import defaultdict
from collections import OrderedDict

from igvfd.metadata.constants import FROM_MATRIX_FILE_SET_FIELDS
from igvfd.metadata.constants import MATRIX_FILE_SET_FILE_LINK_FIELDS
from igvfd.metadata.constants import MATRIX_FILE_SET_METADATA_ALLOWED_TYPES
from igvfd.metadata.constants import METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING
from igvfd.metadata.csv import CSVGenerator
from igvfd.metadata.decorators import allowed_types
from igvfd.metadata.inequalities import map_param_values_to_inequalities
from igvfd.metadata.inequalities import try_to_evaluate_inequality
from igvfd.metadata.search import BatchedSearchGenerator
from igvfd.metadata.serializers import make_experiment_cell
from igvfd.metadata.serializers import make_file_cell
from igvfd.metadata.serializers import map_strings_to_booleans_and_ints

from pyramid.response import Response
from pyramid.view import view_config

from snosearch.interfaces import EXISTS
from snosearch.interfaces import MUST
from snosearch.interfaces import RANGES
from snosearch.parsers import QueryString
from snovault.util import simple_path_ids


# Lattice collection @ids use underscores (not IGVF kebab-case).
FILE_AUDIT_PATH_MARKERS = (
    '/raw_matrix_files/',
    '/processed_matrix_files/',
)


def iter_matrix_file_set_files(file_set):
    files = []
    for field in MATRIX_FILE_SET_FILE_LINK_FIELDS:
        value = file_set.get(field)
        if not value:
            continue
        files.extend(value if isinstance(value, list) else [value])
    return files


def file_matches_file_params(file_, positive_file_param_set):
    # Expects file_param_set where FILES_PREFIX (e.g. 'files.') has been
    # stripped off of key (files.file_type -> file_type)
    # and params with field negation (i.e. file_type!=bigWig)
    # have been filtered out. Param values should be
    # coerced to ints ('2' -> 2) or booleans ('true' -> True)
    # and put into a set for comparison with file values.
    for field, set_of_param_values in positive_file_param_set.items():
        file_value = list(simple_path_ids(file_, field))
        if not file_value:
            return False
        if '*' in set_of_param_values:
            continue
        if not set_of_param_values.intersection(file_value):
            return False
    return True


def some_value_satisfies_inequalities(values, inequalities):
    return all(
        any(
            try_to_evaluate_inequality(inequality, value)
            for value in values
        )
        for inequality in inequalities
    )


def file_satisfies_inequality_constraints(file_, positive_file_inequalities):
    for field, inequalities in positive_file_inequalities.items():
        file_value = list(simple_path_ids(file_, field))
        if not file_value:
            return False
        if not some_value_satisfies_inequalities(file_value, inequalities):
            return False
    return True


def group_audits_by_files_and_type(audits):
    grouped_file_audits = defaultdict(lambda: defaultdict(list))
    grouped_other_audits = defaultdict(list)
    for audit_type, audit_column in METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING:
        for audit in audits.get(audit_type, []):
            path = audit.get('path')
            if path and any(marker in path for marker in FILE_AUDIT_PATH_MARKERS):
                grouped_file_audits[path][audit_type].append(audit.get('category'))
            else:
                grouped_other_audits[audit_type].append(audit.get('category'))
    return grouped_file_audits, grouped_other_audits


class MetadataReport:

    SEARCH_PATH = '/search/'
    EXCLUDED_COLUMNS = (
    )
    DEFAULT_PARAMS = [
        ('field', 'audit'),
        ('field', 'raw_matrix_files'),
        ('field', 'processed_matrix_files'),
        ('limit', 'all'),
    ]
    CONTENT_TYPE = 'text/tsv'
    CONTENT_DISPOSITION = 'attachment; filename="matrix_file_set_metadata.tsv"'
    FILES_PREFIX = 'files.'

    def __init__(self, request):
        self.request = request
        self.query_string = QueryString(request)
        self.param_list = self.query_string.group_values_by_key()
        self.split_file_filters = {}
        self.positive_file_param_set = {}
        self.positive_file_inequalities = {}
        self.header = []
        self.experiment_column_to_fields_mapping = OrderedDict()
        self.file_column_to_fields_mapping = OrderedDict()
        self.csv = CSVGenerator()

    def _get_column_to_fields_mapping(self):
        return FROM_MATRIX_FILE_SET_FIELDS

    def _build_header(self):
        for column in self._get_column_to_fields_mapping():
            if column not in self.EXCLUDED_COLUMNS:
                self.header.append(column)
        for audit, column in METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING:
            self.header.append(column)

    def _split_column_and_fields_by_experiment_and_file(self):
        for column, fields in self._get_column_to_fields_mapping().items():
            if fields[0].startswith(self.FILES_PREFIX):
                self.file_column_to_fields_mapping[column] = [
                    field.replace(self.FILES_PREFIX, '')
                    for field in fields
                ]
            else:
                self.experiment_column_to_fields_mapping[column] = fields

    def _set_split_file_filters(self):
        file_params = self.query_string.get_filters_by_condition(
            key_and_value_condition=lambda k, _: k.startswith(self.FILES_PREFIX)
        )
        self.split_file_filters = self.query_string.split_filters(
            params=file_params
        )

    def _set_positive_file_param_set(self):
        grouped_positive_file_params = self.query_string.group_values_by_key(
            params=self.split_file_filters[MUST] + self.split_file_filters[EXISTS]
        )
        self.positive_file_param_set = {
            k.replace(self.FILES_PREFIX, ''): set(map_strings_to_booleans_and_ints(v))
            for k, v in grouped_positive_file_params.items()
        }

    def _set_positive_file_inequalities(self):
        grouped_positive_file_inequalities = self.query_string.group_values_by_key(
            params=self.split_file_filters[RANGES]
        )
        self.positive_file_inequalities = {
            k.replace(self.FILES_PREFIX, ''): map_param_values_to_inequalities(v)
            for k, v in grouped_positive_file_inequalities.items()
        }

    def _add_fields_to_param_list(self):
        self.param_list['field'] = self.param_list.get('field', [])
        for column, fields in self._get_column_to_fields_mapping().items():
            # Skip logical files.* columns; typed link fields are in DEFAULT_PARAMS.
            if fields[0].startswith(self.FILES_PREFIX):
                continue
            self.param_list['field'].extend(fields)

    def _drop_file_prefix_params_from_query_string(self):
        # Lattice has no files.* property; keep those params for Python-side
        # filtering only and remove them before the OpenSearch request.
        file_params = self.query_string.get_filters_by_condition(
            key_and_value_condition=lambda k, _: k.startswith(self.FILES_PREFIX)
        )
        for key in {k for k, _ in file_params}:
            self.query_string.drop(key)

    def _initialize_at_id_param(self):
        self.param_list['@id'] = self.param_list.get('@id', [])

    def _get_json_elements_or_empty_list(self):
        try:
            return self.request.json.get('elements', [])
        except ValueError:
            return []

    def _maybe_add_json_elements_to_param_list(self):
        self.param_list['@id'].extend(
            self._get_json_elements_or_empty_list()
        )

    def _get_field_params(self):
        return [
            ('field', p)
            for p in self.param_list.get('field', [])
        ]

    def _get_at_id_params(self):
        return [
            ('@id', p)
            for p in self.param_list.get('@id', [])
        ]

    def _get_default_params(self):
        return self.DEFAULT_PARAMS

    def _build_query_string(self):
        self.query_string.drop('limit')
        self.query_string.drop('option')
        self._drop_file_prefix_params_from_query_string()
        self.query_string.extend(
            self._get_default_params()
            + self._get_field_params()
            + self._get_at_id_params()
        )

    def _get_search_path(self):
        return self.SEARCH_PATH

    def _build_new_request(self):
        self._build_query_string()
        request = self.query_string.get_request_with_new_query_string()
        request.path_info = self._get_search_path()
        return request

    def _get_search_results_generator(self):
        return BatchedSearchGenerator(
            self._build_new_request()
        ).results()

    def _should_not_report_file(self, file_):
        conditions = [
            not file_matches_file_params(file_, self.positive_file_param_set),
            not file_satisfies_inequality_constraints(file_, self.positive_file_inequalities),
        ]
        return any(conditions)

    def _get_experiment_data(self, experiment):
        return {
            column: make_experiment_cell(fields, experiment)
            for column, fields in self.experiment_column_to_fields_mapping.items()
        }

    def _get_file_data(self, file_):
        return {
            column: make_file_cell(fields, file_)
            for column, fields in self.file_column_to_fields_mapping.items()
        }

    def _get_audit_data(self, grouped_audits_for_file, grouped_other_audits):
        return {
            audit_column: ', '.join(
                sorted(
                    set(
                        grouped_audits_for_file.get(audit_type, [])
                        + grouped_other_audits.get(audit_type, [])
                    )
                )
            ) for audit_type, audit_column in METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING
        }

    def _output_sorted_row(self, experiment_data, file_data):
        row = []
        for column in self.header:
            row.append(
                file_data.get(
                    column,
                    experiment_data.get(column)
                )
            )
        return row

    def _generate_rows(self):
        yield self.csv.writerow(self.header)
        for file_set in self._get_search_results_generator():
            files = iter_matrix_file_set_files(file_set)
            if not files:
                continue
            grouped_file_audits, grouped_other_audits = group_audits_by_files_and_type(
                file_set.get('audit', {})
            )
            experiment_data = self._get_experiment_data(file_set)
            for file_ in files:
                # Skip unresolved link strings; only report embedded file objects.
                if not isinstance(file_, dict):
                    continue
                if self._should_not_report_file(file_):
                    continue
                file_data = self._get_file_data(file_)
                audit_data = self._get_audit_data(
                    grouped_file_audits.get(file_.get('@id'), {}),
                    grouped_other_audits
                )
                file_data.update(audit_data)
                yield self.csv.writerow(
                    self._output_sorted_row(experiment_data, file_data)
                )

    def _initialize_report(self):
        self._build_header()
        self._split_column_and_fields_by_experiment_and_file()
        self._set_split_file_filters()
        self._set_positive_file_param_set()
        self._set_positive_file_inequalities()

    def _build_params(self):
        self._add_fields_to_param_list()
        self._initialize_at_id_param()
        self._maybe_add_json_elements_to_param_list()

    def generate(self):
        self._initialize_report()
        self._build_params()
        return Response(
            content_type=self.CONTENT_TYPE,
            app_iter=self._generate_rows(),
            content_disposition=self.CONTENT_DISPOSITION,
        )


@view_config(route_name='matrix-file-set-metadata', request_method=['GET', 'POST'])
@allowed_types(MATRIX_FILE_SET_METADATA_ALLOWED_TYPES)
def matrix_file_set_metadata_tsv(context, request):
    return MetadataReport(request).generate()
