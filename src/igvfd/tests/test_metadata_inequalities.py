import pytest

from igvfd.metadata.inequalities import map_param_values_to_inequalities
from igvfd.metadata.inequalities import parse_inequality_param_value
from igvfd.metadata.inequalities import try_to_evaluate_inequality
from igvfd.metadata.metadata import file_satisfies_inequality_constraints
from igvfd.metadata.metadata import some_value_satisfies_inequalities


def test_parse_inequality_param_value():
    assert parse_inequality_param_value('gt:12000') == ['gt', '12000']


@pytest.mark.parametrize(
    'relation, right_operand, left_operand, expected',
    [
        ('gt', '12000', 12001, True),
        ('gt', '12000', 12000, False),
        ('gte', '12000', 12000, True),
        ('lt', '12000', 11999, True),
        ('lte', '12000', 12000, True),
    ],
)
def test_map_param_values_to_inequalities(relation, right_operand, left_operand, expected):
    inequalities = map_param_values_to_inequalities([f'{relation}:{right_operand}'])
    assert len(inequalities) == 1
    assert inequalities[0](left_operand) is expected


def test_try_to_evaluate_inequality_returns_false_on_type_error():
    inequalities = map_param_values_to_inequalities(['gt:12000'])
    assert try_to_evaluate_inequality(inequalities[0], 'not-a-number') is False


def test_some_value_satisfies_inequalities_any_value_matches():
    inequalities = map_param_values_to_inequalities(['gte:12000'])
    assert some_value_satisfies_inequalities([11000, 12000], inequalities) is True
    assert some_value_satisfies_inequalities([11000, 11500], inequalities) is False


def test_file_satisfies_inequality_constraints():
    inequalities = {
        'observation_count': map_param_values_to_inequalities(['gte:12000']),
    }
    assert file_satisfies_inequality_constraints(
        {'observation_count': 12000},
        inequalities,
    ) is True
    assert file_satisfies_inequality_constraints(
        {'observation_count': 11500},
        inequalities,
    ) is False
    assert file_satisfies_inequality_constraints({}, inequalities) is False
