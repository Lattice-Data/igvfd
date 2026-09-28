from snovault.upgrader import upgrade_step

from .aliases import preserve_invalid_aliases

_CXG_PLACEHOLDER = 'placeholder cxg donor id'


@upgrade_step('human_donor', '1', '2')
def human_donor_1_2(value, system):
    if 'cxg_donor_id' not in value or value['cxg_donor_id'] in (None, ''):
        value['cxg_donor_id'] = _CXG_PLACEHOLDER


@upgrade_step('non_human_donor', '1', '2')
def non_human_donor_1_2(value, system):
    if 'cxg_donor_id' not in value or value['cxg_donor_id'] in (None, ''):
        value['cxg_donor_id'] = _CXG_PLACEHOLDER


@upgrade_step('human_donor', '2', '3')
def human_donor_2_3(value, system):
    preserve_invalid_aliases(value)


@upgrade_step('non_human_donor', '2', '3')
def non_human_donor_2_3(value, system):
    preserve_invalid_aliases(value)
