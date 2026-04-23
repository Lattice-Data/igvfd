from snovault.upgrader import upgrade_step


@upgrade_step('controlled_term', '1', '2')
def controlled_term_1_2(value, system):
    value.pop('term_name', None)
