from snovault.upgrader import upgrade_step


MULTIPLEXING_METHOD_MAP = {
    'cell hashing': 'antibody hashing',
    'lipid hashing': 'lipid hashing',
    'genetic': 'natural genetic variation',
    'sample barcodes': 'probe barcoding',
}

DROPLET_REMOVED_PROPERTIES = (
    'chemistry_version',
    'cell_barcode_length',
    'umi_length',
)

PLATE_REMOVED_PROPERTIES = (
    'kit_version',
    'indexing_rounds',
)


def _upgrade_multiplexing_method(value):
    legacy = value.pop('multiplexing_method', None)
    if legacy is None:
        return
    if isinstance(legacy, list):
        return
    mapped = MULTIPLEXING_METHOD_MAP.get(legacy)
    if mapped is None:
        raise ValueError(f'Unknown multiplexing_method {legacy!r}')
    value['multiplexing_method'] = [mapped]


def _drop_properties(value, property_names):
    for name in property_names:
        value.pop(name, None)


@upgrade_step('droplet_based_library', '1', '2')
def droplet_based_library_1_2(value, system):
    _drop_properties(value, DROPLET_REMOVED_PROPERTIES)
    _upgrade_multiplexing_method(value)


@upgrade_step('plate_based_library', '1', '2')
def plate_based_library_1_2(value, system):
    _drop_properties(value, PLATE_REMOVED_PROPERTIES)
    _upgrade_multiplexing_method(value)
