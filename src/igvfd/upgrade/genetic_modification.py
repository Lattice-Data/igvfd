from snovault.upgrader import upgrade_step


MODALITY_TO_STRATEGY = {
    'activation': 'activation screen',
    'base editing': 'base editing screen',
    'cutting': 'cutting screen',
    'interference': 'interference screen',
    'knockout': 'knockout screen',
    'localizing': 'localizing screen',
    'prime editing': 'prime editing screen',
}


@upgrade_step('genetic_modification', '1', '2')
def genetic_modification_1_2(value, system):
    if 'modality' not in value:
        return
    legacy = value.pop('modality')
    mapped = MODALITY_TO_STRATEGY.get(legacy)
    if mapped is None:
        raise ValueError(f'Unknown genetic_modification modality {legacy!r}')
    value['strategy'] = mapped
