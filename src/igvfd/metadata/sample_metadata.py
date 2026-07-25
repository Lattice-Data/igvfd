from igvfd.metadata.constants import BIOSAMPLE_METADATA_FIELDS
from igvfd.metadata.constants import FROM_BIOSAMPLE_COLUMNS
from igvfd.metadata.constants import INTENDED_CELL_TYPE_SAMPLE_TYPES
from igvfd.metadata.constants import MATRIX_FILE_SET_FILE_LINK_FIELDS
from igvfd.metadata.constants import MATRIX_FILE_SET_SAMPLE_METADATA_ALLOWED_TYPES
from igvfd.metadata.constants import METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING
from igvfd.metadata.constants import SAMPLE_METADATA_PLACEHOLDER
from igvfd.metadata.constants import SAMPLE_TYPE_LABELS
from igvfd.metadata.constants import SAMPLE_VALUE_SEPARATOR
from igvfd.metadata.csv import CSVGenerator
from igvfd.metadata.decorators import allowed_types
from igvfd.metadata.search import BatchedSearchGenerator

from pyramid.response import Response
from pyramid.view import view_config

from snosearch.parsers import QueryString
from snovault.util import simple_path_ids


def clean_alias(value):
    # Lattice aliases are 'lab:identifier'. Submission templates want the bare
    # identifier, matching lattice-tools DB2Flattener._get_clean_alias.
    text = str(value)
    if ':' in text:
        return text.split(':', 1)[1]
    return text


def join_sample_values(values):
    unique = set()
    for value in values:
        text = str(value).strip()
        if text:
            unique.add(text)
    return SAMPLE_VALUE_SEPARATOR.join(sorted(unique))


def get_concrete_type(sample):
    types = sample.get('@type') or []
    for type_name in types:
        if type_name in SAMPLE_TYPE_LABELS:
            return type_name
    return ''


def iter_embedded_objects(sample, field):
    value = sample.get(field)
    if not value:
        return
    for item in value if isinstance(value, list) else [value]:
        # Unresolved links are plain @id strings; only composed cells need objects.
        if isinstance(item, dict):
            yield item


def render_treatment(sample, concrete_type):
    cells = []
    for treatment in iter_embedded_objects(sample, 'treatments'):
        parts = []
        term = treatment.get('ontological_term')
        if isinstance(term, dict) and term.get('term_name'):
            parts.append(str(term['term_name']))
        amount = treatment.get('amount')
        amount_units = treatment.get('amount_units')
        if amount is not None and amount_units:
            parts.append(f'{amount} {amount_units}')
        if parts:
            cells.append(' '.join(parts))
    return join_sample_values(cells)


def render_perturbation_timepoint(sample, concrete_type):
    cells = []
    for treatment in iter_embedded_objects(sample, 'treatments'):
        lower = treatment.get('lower_bound_duration')
        upper = treatment.get('upper_bound_duration')
        units = treatment.get('duration_units')
        if lower is None or not units:
            continue
        span = str(lower) if upper is None or upper == lower else f'{lower}-{upper}'
        cells.append(f'{span} {units}')
    return join_sample_values(cells)


def render_perturbation_factors(sample, concrete_type):
    cells = []
    for condition in iter_embedded_objects(sample, 'experimental_conditions'):
        parts = []
        if condition.get('condition'):
            parts.append(str(condition['condition']))
        if condition.get('text_value'):
            parts.append(str(condition['text_value']))
        elif condition.get('value') is not None:
            value = str(condition['value'])
            if condition.get('units'):
                value = f"{value} {condition['units']}"
            parts.append(value)
        if parts:
            cells.append(' '.join(parts))
    return join_sample_values(cells)


def render_cell_subtype(sample, concrete_type):
    field = (
        'intended_cell_types'
        if concrete_type in INTENDED_CELL_TYPE_SAMPLE_TYPES
        else 'enriched_cell_types'
    )
    return join_sample_values(simple_path_ids(sample, f'{field}.term_name'))


def render_sample_type(sample, concrete_type):
    return SAMPLE_TYPE_LABELS.get(concrete_type, '')


def render_library_id(sample, concrete_type):
    # libraries is an embedded reverse link; CRO_group_identifier is the submitter
    # facing library name, so libraries without one contribute nothing.
    return join_sample_values(simple_path_ids(sample, 'libraries.CRO_group_identifier'))


SAMPLE_CELL_RENDERERS = {
    'cell_subtype': render_cell_subtype,
    'library_id': render_library_id,
    'perturbation_factors': render_perturbation_factors,
    'perturbation_timepoint': render_perturbation_timepoint,
    'sample_type': render_sample_type,
    'treatment': render_treatment,
}


def make_sample_cell(spec, sample, concrete_type):
    if spec.get('placeholder'):
        return SAMPLE_METADATA_PLACEHOLDER
    renderer = spec.get('render')
    if renderer:
        return SAMPLE_CELL_RENDERERS[renderer](sample, concrete_type)
    allowed_sample_types = spec.get('types')
    if allowed_sample_types and concrete_type not in allowed_sample_types:
        return ''
    values = list(simple_path_ids(sample, spec['path']))
    if spec.get('clean_alias'):
        values = [clean_alias(value) for value in values]
    return join_sample_values(values)


def collect_sample_ids(file_sets):
    # Phase A: one hop. Matrix files embed their samples, so the deduped set of
    # biosample @ids is read straight off the already-embedded objects.
    sample_ids = []
    seen = set()
    for file_set in file_sets:
        for link_field in MATRIX_FILE_SET_FILE_LINK_FIELDS:
            value = file_set.get(link_field)
            if not value:
                continue
            for file_ in value if isinstance(value, list) else [value]:
                if not isinstance(file_, dict):
                    continue
                for sample in file_.get('samples') or []:
                    at_id = sample.get('@id') if isinstance(sample, dict) else sample
                    if at_id and at_id not in seen:
                        seen.add(at_id)
                        sample_ids.append(at_id)
    return sample_ids


class SampleMetadataReport:

    SEARCH_PATH = '/search/'
    CONTENT_TYPE = 'text/tsv'
    CONTENT_DISPOSITION = 'attachment; filename="matrix_file_set_sample_metadata.tsv"'
    BIOSAMPLE_SEARCH_TYPE = 'Biosample'
    FILE_SET_PARAMS = [
        ('field', 'raw_matrix_files'),
        ('field', 'processed_matrix_files'),
        ('limit', 'all'),
    ]

    def __init__(self, request):
        self.request = request
        self.header = []
        self.csv = CSVGenerator()

    def _build_header(self):
        self.header = list(FROM_BIOSAMPLE_COLUMNS)
        for _, audit_column in METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING:
            self.header.append(audit_column)

    def _get_json_elements_or_empty_list(self):
        try:
            return self.request.json.get('elements', [])
        except ValueError:
            return []

    def _new_query_string(self, drop_all=False):
        # QueryString parses the incoming request and never mutates it, so each call
        # yields an independent copy that can be reshaped for a different search.
        query_string = QueryString(self.request)
        if drop_all:
            for key in list(query_string.group_values_by_key()):
                query_string.drop(key)
        else:
            query_string.drop('limit')
            query_string.drop('option')
            query_string.drop('field')
        return query_string

    def _build_request(self, query_string):
        request = query_string.get_request_with_new_query_string()
        request.path_info = self.SEARCH_PATH
        request.registry = self.request.registry
        return request

    def _get_file_set_results(self):
        query_string = self._new_query_string()
        at_id_params = [
            ('@id', element)
            for element in self._get_json_elements_or_empty_list()
        ]
        query_string.extend(self.FILE_SET_PARAMS + at_id_params)
        return BatchedSearchGenerator(self._build_request(query_string)).results()

    def _get_sample_results(self, sample_ids):
        # The MatrixFileSet filters must not leak into the Biosample search, so the
        # incoming query is dropped entirely and rebuilt.
        query_string = self._new_query_string(drop_all=True)
        query_string.extend(
            [('type', self.BIOSAMPLE_SEARCH_TYPE)]
            + [('@id', sample_id) for sample_id in sample_ids]
            + [('field', field) for field in BIOSAMPLE_METADATA_FIELDS]
            + [('limit', 'all')]
        )
        return BatchedSearchGenerator(self._build_request(query_string)).results()

    def _get_audit_data(self, sample):
        audits = sample.get('audit') or {}
        return {
            audit_column: ', '.join(
                sorted({
                    audit.get('category', '')
                    for audit in audits.get(audit_type, [])
                })
            )
            for audit_type, audit_column in METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING
        }

    def _get_sample_row(self, sample):
        concrete_type = get_concrete_type(sample)
        row_data = {
            column: make_sample_cell(spec, sample, concrete_type)
            for column, spec in FROM_BIOSAMPLE_COLUMNS.items()
        }
        row_data.update(self._get_audit_data(sample))
        return [row_data.get(column, '') for column in self.header]

    def _generate_rows(self):
        yield self.csv.writerow(self.header)
        sample_ids = collect_sample_ids(self._get_file_set_results())
        if not sample_ids:
            return
        for sample in self._get_sample_results(sample_ids):
            yield self.csv.writerow(self._get_sample_row(sample))

    def generate(self):
        self._build_header()
        return Response(
            content_type=self.CONTENT_TYPE,
            app_iter=self._generate_rows(),
            content_disposition=self.CONTENT_DISPOSITION,
        )


@view_config(route_name='matrix-file-set-sample-metadata', request_method=['GET', 'POST'])
@allowed_types(MATRIX_FILE_SET_SAMPLE_METADATA_ALLOWED_TYPES)
def matrix_file_set_sample_metadata_tsv(context, request):
    return SampleMetadataReport(request).generate()
