from collections import defaultdict
from collections import OrderedDict

from igvfd.metadata.constants import FROM_MATRIX_FILE_COLUMNS
from igvfd.metadata.constants import FROM_MATRIX_FILE_SET_COLUMNS
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

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid.view import view_config

from snosearch.interfaces import EXISTS
from snosearch.interfaces import MUST
from snosearch.interfaces import MUST_NOT
from snosearch.interfaces import NOT_EXISTS
from snosearch.interfaces import NOT_RANGES
from snosearch.interfaces import RANGES
from snosearch.parsers import QueryString
from snovault.util import simple_path_ids


# Lattice collection @ids use underscores (not IGVF kebab-case).
FILE_AUDIT_PATH_MARKERS = (
    '/raw_matrix_files/',
    '/processed_matrix_files/',
)


def parse_file_link_filter_key(key):
    for link_field in MATRIX_FILE_SET_FILE_LINK_FIELDS:
        prefix = f'{link_field}.'
        if key.startswith(prefix):
            return link_field, key[len(prefix):]
    return None, None


def file_matches_file_params(file_, positive_file_param_set):
    # Expects positive_file_param_set keyed by file property names on the
    # embedded file object. Negated link filters are rejected during report init.
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
    EXCLUDED_COLUMNS = ()
    DEFAULT_PARAMS = [
        ('field', 'audit'),
        ('field', 'raw_matrix_files'),
        ('field', 'processed_matrix_files'),
        ('limit', 'all'),
    ]
    CONTENT_TYPE = 'text/tsv'
    CONTENT_DISPOSITION = 'attachment; filename="matrix_file_set_metadata.tsv"'
    LEGACY_FILES_PREFIX = 'files.'
    _UNSUPPORTED_FILE_FILTER_BUCKETS = (MUST_NOT, NOT_EXISTS, NOT_RANGES)

    def __init__(self, request):
        self.request = request
        self.query_string = QueryString(request)
        self.param_list = self.query_string.group_values_by_key()
        self.split_file_filters = {}
        self.positive_file_param_set_by_link = {
            link_field: {} for link_field in MATRIX_FILE_SET_FILE_LINK_FIELDS
        }
        self.positive_file_inequalities_by_link = {
            link_field: {} for link_field in MATRIX_FILE_SET_FILE_LINK_FIELDS
        }
        self.filtered_link_fields = set()
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
        self.file_column_to_fields_mapping = OrderedDict(FROM_MATRIX_FILE_COLUMNS)
        self.experiment_column_to_fields_mapping = OrderedDict(FROM_MATRIX_FILE_SET_COLUMNS)

    def _set_split_file_filters(self):
        file_params = self.query_string.get_filters_by_condition(
            key_and_value_condition=lambda k, _: parse_file_link_filter_key(k)[0] is not None
        )
        self.split_file_filters = self.query_string.split_filters(
            params=file_params
        )

    def _reject_legacy_files_filters(self):
        legacy_filters = self.query_string.get_filters_by_condition(
            key_and_value_condition=lambda k, _: k.startswith(self.LEGACY_FILES_PREFIX)
        )
        if legacy_filters:
            raise HTTPBadRequest(
                explanation=(
                    'files.* filters are not supported. '
                    'Use raw_matrix_files.* or processed_matrix_files.* instead.'
                )
            )

    def _reject_unsupported_file_filters(self):
        unsupported = []
        for bucket in self._UNSUPPORTED_FILE_FILTER_BUCKETS:
            unsupported.extend(self.split_file_filters.get(bucket, []))
        if unsupported:
            raise HTTPBadRequest(
                explanation='Negated raw_matrix_files.* and processed_matrix_files.* filters are not supported.'
            )

    def _set_positive_file_param_set(self):
        grouped_positive_file_params = self.query_string.group_values_by_key(
            params=self.split_file_filters[MUST] + self.split_file_filters[EXISTS]
        )
        for key, values in grouped_positive_file_params.items():
            link_field, file_field = parse_file_link_filter_key(key)
            if link_field is None:
                continue
            self.positive_file_param_set_by_link[link_field][file_field] = set(
                map_strings_to_booleans_and_ints(values)
            )

    def _set_positive_file_inequalities(self):
        grouped_positive_file_inequalities = self.query_string.group_values_by_key(
            params=self.split_file_filters[RANGES]
        )
        for key, values in grouped_positive_file_inequalities.items():
            link_field, file_field = parse_file_link_filter_key(key)
            if link_field is None:
                continue
            self.positive_file_inequalities_by_link[link_field][file_field] = (
                map_param_values_to_inequalities(values)
            )

    def _add_fields_to_param_list(self):
        self.param_list['field'] = self.param_list.get('field', [])
        for column, fields in self.experiment_column_to_fields_mapping.items():
            self.param_list['field'].extend(fields)

    def _drop_file_link_filter_params_from_query_string(self):
        # Nested link filters are applied in Python; remove them before OpenSearch.
        file_params = self.query_string.get_filters_by_condition(
            key_and_value_condition=lambda k, _: parse_file_link_filter_key(k)[0] is not None
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
        self._drop_file_link_filter_params_from_query_string()
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

    def _set_filtered_link_fields(self):
        # Link fields that carry at least one positive filter. When any exist, a
        # filter naming one array (e.g. processed_matrix_files.*) scopes output to
        # that array only; files in unfiltered link fields are excluded entirely.
        self.filtered_link_fields = {
            link_field
            for link_field in MATRIX_FILE_SET_FILE_LINK_FIELDS
            if self.positive_file_param_set_by_link.get(link_field)
            or self.positive_file_inequalities_by_link.get(link_field)
        }

    def _should_not_report_file(self, file_, link_field):
        if self.filtered_link_fields and link_field not in self.filtered_link_fields:
            return True
        positive_file_param_set = self.positive_file_param_set_by_link.get(link_field, {})
        positive_file_inequalities = self.positive_file_inequalities_by_link.get(link_field, {})
        if not positive_file_param_set and not positive_file_inequalities:
            return False
        conditions = []
        if positive_file_param_set:
            conditions.append(
                not file_matches_file_params(file_, positive_file_param_set)
            )
        if positive_file_inequalities:
            conditions.append(
                not file_satisfies_inequality_constraints(file_, positive_file_inequalities)
            )
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
            if not any(
                file_set.get(link_field)
                for link_field in MATRIX_FILE_SET_FILE_LINK_FIELDS
            ):
                continue
            grouped_file_audits, grouped_other_audits = group_audits_by_files_and_type(
                file_set.get('audit', {})
            )
            experiment_data = self._get_experiment_data(file_set)
            for link_field in MATRIX_FILE_SET_FILE_LINK_FIELDS:
                value = file_set.get(link_field)
                if not value:
                    continue
                for file_ in value if isinstance(value, list) else [value]:
                    # Skip unresolved link strings; only report embedded file objects.
                    if not isinstance(file_, dict):
                        continue
                    if self._should_not_report_file(file_, link_field):
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
        self._reject_legacy_files_filters()
        self._set_split_file_filters()
        self._reject_unsupported_file_filters()
        self._set_positive_file_param_set()
        self._set_positive_file_inequalities()
        self._set_filtered_link_fields()

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
