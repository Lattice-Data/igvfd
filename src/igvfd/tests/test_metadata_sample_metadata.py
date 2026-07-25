import pytest

from igvfd.metadata.sample_metadata import clean_alias
from igvfd.metadata.sample_metadata import collect_sample_ids
from igvfd.metadata.sample_metadata import get_concrete_type
from igvfd.metadata.sample_metadata import iter_embedded_objects
from igvfd.metadata.sample_metadata import join_sample_values
from igvfd.metadata.sample_metadata import make_sample_cell
from igvfd.metadata.sample_metadata import render_cell_subtype
from igvfd.metadata.sample_metadata import render_library_id
from igvfd.metadata.sample_metadata import render_perturbation_factors
from igvfd.metadata.sample_metadata import render_perturbation_timepoint
from igvfd.metadata.sample_metadata import render_sample_type
from igvfd.metadata.sample_metadata import render_treatment


@pytest.mark.parametrize(
    'value,expected',
    [
        ('lattice:tissue-frozen-basic', 'tissue-frozen-basic'),
        ('jonathan-weissman:yhc_viral_smORF_1', 'yhc_viral_smORF_1'),
        # Only the first colon delimits the lab prefix.
        ('lattice:has:colons', 'has:colons'),
        # A value with no prefix is passed through untouched.
        ('no-prefix', 'no-prefix'),
        ('', ''),
    ],
)
def test_clean_alias(value, expected):
    assert clean_alias(value) == expected


def test_join_sample_values_sorts_dedupes_and_drops_blanks():
    assert join_sample_values(['b', 'a']) == 'a; b'
    assert join_sample_values(['a', 'a']) == 'a'
    assert join_sample_values(['a', '', '  ', ' b ']) == 'a; b'
    assert join_sample_values([]) == ''
    # Non-string values are coerced, so numeric fields render without error.
    assert join_sample_values([2, 10]) == '10; 2'


@pytest.mark.parametrize(
    'types,expected',
    [
        (['Tissue', 'Biosample', 'Item'], 'Tissue'),
        (['CellLine', 'Biosample', 'Item'], 'CellLine'),
        (['Organoid', 'Biosample', 'Item'], 'Organoid'),
        (['PrimaryCellCulture', 'Biosample', 'Item'], 'PrimaryCellCulture'),
        # Abstract-only or unknown @type yields no concrete type.
        (['Biosample', 'Item'], ''),
        ([], ''),
    ],
)
def test_get_concrete_type(types, expected):
    assert get_concrete_type({'@type': types}) == expected


def test_get_concrete_type_missing_key():
    assert get_concrete_type({}) == ''


def test_iter_embedded_objects_skips_unresolved_links():
    sample = {
        'treatments': [{'@id': '/treatments/a/'}, '/treatments/b/'],
        'genetic_modification': {'@id': '/genetic_modifications/c/'},
        'empty': [],
    }
    # Plain @id strings are unresolved links and cannot supply composed fields.
    assert list(iter_embedded_objects(sample, 'treatments')) == [{'@id': '/treatments/a/'}]
    # A scalar link is wrapped, so scalar and array embeds are handled alike.
    assert list(iter_embedded_objects(sample, 'genetic_modification')) == [
        {'@id': '/genetic_modifications/c/'}
    ]
    assert list(iter_embedded_objects(sample, 'empty')) == []
    assert list(iter_embedded_objects(sample, 'absent')) == []


def test_render_treatment_composes_agent_and_amount():
    sample = {
        'treatments': [
            {
                'ontological_term': {'term_name': 'vitamin D'},
                'amount': 10,
                'amount_units': 'mg/kg',
            }
        ]
    }
    assert render_treatment(sample, 'Tissue') == 'vitamin D 10 mg/kg'


def test_render_treatment_omits_amount_without_units():
    sample = {'treatments': [{'ontological_term': {'term_name': 'vitamin D'}, 'amount': 10}]}
    assert render_treatment(sample, 'Tissue') == 'vitamin D'


def test_render_treatment_keeps_treatments_separate():
    # The composed value must be built per treatment; pairing fields across objects
    # is exactly the corruption a multi-path column list would introduce.
    sample = {
        'treatments': [
            {'ontological_term': {'term_name': 'vitamin D'}, 'amount': 10, 'amount_units': 'mg/kg'},
            {'ontological_term': {'term_name': 'retinol'}, 'amount': 5, 'amount_units': 'nM'},
        ]
    }
    assert render_treatment(sample, 'Tissue') == 'retinol 5 nM; vitamin D 10 mg/kg'


def test_render_treatment_empty_without_treatments():
    assert render_treatment({}, 'Tissue') == ''
    assert render_treatment({'treatments': [{}]}, 'Tissue') == ''


def test_render_perturbation_timepoint_collapses_equal_bounds():
    sample = {
        'treatments': [
            {'lower_bound_duration': 24, 'upper_bound_duration': 24, 'duration_units': 'hour'}
        ]
    }
    assert render_perturbation_timepoint(sample, 'Tissue') == '24 hour'


def test_render_perturbation_timepoint_renders_span():
    sample = {
        'treatments': [
            {'lower_bound_duration': 24, 'upper_bound_duration': 48, 'duration_units': 'hour'}
        ]
    }
    assert render_perturbation_timepoint(sample, 'Tissue') == '24-48 hour'


def test_render_perturbation_timepoint_keeps_units_with_own_treatment():
    # Two timed treatments must not cross bounds or lose a unit.
    sample = {
        'treatments': [
            {'lower_bound_duration': 24, 'upper_bound_duration': 48, 'duration_units': 'hour'},
            {'lower_bound_duration': 6, 'upper_bound_duration': 6, 'duration_units': 'day'},
        ]
    }
    assert render_perturbation_timepoint(sample, 'Tissue') == '24-48 hour; 6 day'


def test_render_perturbation_timepoint_requires_units_and_lower_bound():
    assert render_perturbation_timepoint(
        {'treatments': [{'lower_bound_duration': 24}]}, 'Tissue'
    ) == ''
    assert render_perturbation_timepoint(
        {'treatments': [{'duration_units': 'hour'}]}, 'Tissue'
    ) == ''


def test_render_perturbation_factors_prefers_text_value():
    sample = {
        'experimental_conditions': [
            {'condition': 'diet', 'text_value': 'high fat', 'value': 9, 'units': 'percent'}
        ]
    }
    assert render_perturbation_factors(sample, 'Tissue') == 'diet high fat'


def test_render_perturbation_factors_uses_value_and_units():
    sample = {
        'experimental_conditions': [
            {'condition': 'temperature', 'value': 37, 'units': 'celsius'},
            {'condition': 'pH', 'value': 7.4, 'units': 'pH units'},
        ]
    }
    assert render_perturbation_factors(sample, 'Tissue') == (
        'pH 7.4 pH units; temperature 37 celsius'
    )


def test_render_perturbation_factors_value_without_units():
    sample = {'experimental_conditions': [{'condition': 'oxygen level', 'value': 5}]}
    assert render_perturbation_factors(sample, 'Tissue') == 'oxygen level 5'


def test_render_perturbation_factors_empty():
    assert render_perturbation_factors({}, 'Tissue') == ''


@pytest.mark.parametrize(
    'concrete_type,expected',
    [
        ('CellLine', 'intended'),
        ('Organoid', 'intended'),
        ('Tissue', 'enriched'),
        ('PrimaryCellCulture', 'enriched'),
    ],
)
def test_render_cell_subtype_source_depends_on_type(concrete_type, expected):
    sample = {
        'intended_cell_types': [{'term_name': 'intended'}],
        'enriched_cell_types': [{'term_name': 'enriched'}],
    }
    assert render_cell_subtype(sample, concrete_type) == expected


def test_render_cell_subtype_blank_when_source_absent():
    # Tissue has no intended_cell_types property, so an intended-only sample is blank.
    sample = {'intended_cell_types': [{'term_name': 'intended'}]}
    assert render_cell_subtype(sample, 'Tissue') == ''


@pytest.mark.parametrize(
    'concrete_type,expected',
    [
        ('Tissue', 'tissue'),
        ('PrimaryCellCulture', 'primary cell culture'),
        ('Organoid', 'organoid'),
        ('CellLine', 'cell line'),
        ('', ''),
    ],
)
def test_render_sample_type(concrete_type, expected):
    assert render_sample_type({}, concrete_type) == expected


def test_render_library_id_uses_cro_group_identifier():
    sample = {
        'libraries': [
            {'@id': '/droplet_based_libraries/a/', 'CRO_group_identifier': 'GROUP-2'},
            {'@id': '/plate_based_libraries/b/', 'CRO_group_identifier': 'GROUP-1'},
            # A library without the identifier contributes nothing.
            {'@id': '/plate_based_libraries/c/'},
        ]
    }
    assert render_library_id(sample, 'Tissue') == 'GROUP-1; GROUP-2'


def test_render_library_id_empty():
    assert render_library_id({}, 'Tissue') == ''
    assert render_library_id({'libraries': [{'@id': '/plate_based_libraries/c/'}]}, 'Tissue') == ''


def test_make_sample_cell_placeholder_ignores_the_object():
    assert make_sample_cell({'placeholder': True}, {}, 'Tissue') == 'placeholder'


def test_make_sample_cell_simple_and_nested_paths():
    sample = {
        'description': 'a description',
        'donors': [{'taxa': 'Homo sapiens'}],
    }
    assert make_sample_cell({'path': 'description'}, sample, 'Tissue') == 'a description'
    assert make_sample_cell({'path': 'donors.taxa'}, sample, 'Tissue') == 'Homo sapiens'
    # An unresolvable path is a blank cell, not an error.
    assert make_sample_cell({'path': 'absent'}, sample, 'Tissue') == ''


def test_make_sample_cell_strips_alias_prefix():
    sample = {'aliases': ['lattice:second', 'lattice:first']}
    assert make_sample_cell(
        {'path': 'aliases', 'clean_alias': True}, sample, 'Tissue'
    ) == 'first; second'


def test_make_sample_cell_type_gating():
    sample = {'sample_terms': [{'term_name': 'uterine cervix'}]}
    spec = {'path': 'sample_terms.term_name', 'types': ('Tissue', 'Organoid')}
    assert make_sample_cell(spec, sample, 'Tissue') == 'uterine cervix'
    assert make_sample_cell(spec, sample, 'Organoid') == 'uterine cervix'
    # Off-type rows render blank even though the underlying value exists.
    assert make_sample_cell(spec, sample, 'CellLine') == ''
    assert make_sample_cell(spec, sample, '') == ''


def test_make_sample_cell_dispatches_to_renderer():
    assert make_sample_cell({'render': 'sample_type'}, {}, 'CellLine') == 'cell line'


def test_collect_sample_ids_dedupes_across_files_and_link_fields():
    file_sets = [
        {
            'raw_matrix_files': [
                {'samples': [{'@id': '/tissues/a/'}]},
                {'samples': [{'@id': '/tissues/a/'}, {'@id': '/tissues/b/'}]},
            ],
            'processed_matrix_files': [
                {'samples': [{'@id': '/tissues/b/'}, {'@id': '/cell_lines/c/'}]},
            ],
        }
    ]
    # First-seen order is preserved so output rows are stable between requests.
    assert collect_sample_ids(file_sets) == ['/tissues/a/', '/tissues/b/', '/cell_lines/c/']


def test_collect_sample_ids_dedupes_across_file_sets():
    file_sets = [
        {'raw_matrix_files': [{'samples': [{'@id': '/tissues/a/'}]}]},
        {'raw_matrix_files': [{'samples': [{'@id': '/tissues/a/'}]}]},
    ]
    assert collect_sample_ids(file_sets) == ['/tissues/a/']


def test_collect_sample_ids_accepts_unresolved_sample_links():
    file_sets = [{'raw_matrix_files': [{'samples': ['/tissues/a/']}]}]
    assert collect_sample_ids(file_sets) == ['/tissues/a/']


def test_collect_sample_ids_skips_files_without_samples():
    file_sets = [
        {'processed_matrix_files': [{'@id': '/processed_matrix_files/a/'}]},
        {'raw_matrix_files': [{'samples': []}]},
    ]
    assert collect_sample_ids(file_sets) == []


def test_collect_sample_ids_skips_unresolved_file_links():
    # A file that did not embed is a bare @id string and carries no samples.
    file_sets = [{'raw_matrix_files': ['/raw_matrix_files/a/']}]
    assert collect_sample_ids(file_sets) == []


def test_collect_sample_ids_handles_file_sets_without_files():
    assert collect_sample_ids([{}]) == []
    assert collect_sample_ids([]) == []
