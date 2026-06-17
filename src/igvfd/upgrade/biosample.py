from snovault.upgrader import upgrade_step


ENRICHMENT_METHOD_TO_SELECTION_METHOD = {
    'FACS': 'FACS',
    'MACS': 'MACS',
    'size exclusion': 'size selection',
    'density gradient': 'density gradient',
    'manual picking': 'manual selection',
    'microfluidics': 'microfluidics',
}

# Legacy expression_level -> suffix for CD{n} markers (positive/intermediate -> +; negative -> -;
# low/high -> + per biosample schema version 2 migration).
_EXPRESSION_SUFFIX = {
    'negative': '-',
    'positive': '+',
    'intermediate': '+',
    'low': '+',
    'high': '+',
}


def _upgrade_biosample_properties(value):
    if 'enrichment_method' in value:
        legacy_method = value.pop('enrichment_method')
        mapped = ENRICHMENT_METHOD_TO_SELECTION_METHOD.get(legacy_method)
        if mapped is not None:
            value['selection_methods'] = [mapped]

    if 'enrichment_markers' in value:
        legacy_markers = value.pop('enrichment_markers')
        tokens = []
        for row in legacy_markers:
            marker = row['marker']
            expr = row['expression_level']
            suffix = _EXPRESSION_SUFFIX.get(expr)
            if suffix is None:
                raise ValueError(
                    f'Unknown enrichment_markers expression_level {expr!r} for marker {marker!r}'
                )
            tokens.append(f'{marker}{suffix}')
        deduped_sorted = sorted(set(tokens))
        if deduped_sorted:
            value['selection_markers'] = deduped_sorted


@upgrade_step('tissue', '1', '2')
def tissue_1_2(value, system):
    _upgrade_biosample_properties(value)


@upgrade_step('primary_cell_culture', '1', '2')
def primary_cell_culture_1_2(value, system):
    _upgrade_biosample_properties(value)


@upgrade_step('organoid', '1', '2')
def organoid_1_2(value, system):
    _upgrade_biosample_properties(value)


@upgrade_step('cell_line', '1', '2')
def cell_line_1_2(value, system):
    _upgrade_biosample_properties(value)


def _upgrade_hash_index_to_multiplexing_barcodes(value):
    if 'hash_index' in value:
        value['multiplexing_barcodes'] = [value.pop('hash_index')]


@upgrade_step('tissue', '2', '3')
def tissue_2_3(value, system):
    _upgrade_hash_index_to_multiplexing_barcodes(value)


@upgrade_step('primary_cell_culture', '2', '3')
def primary_cell_culture_2_3(value, system):
    _upgrade_hash_index_to_multiplexing_barcodes(value)


@upgrade_step('organoid', '2', '3')
def organoid_2_3(value, system):
    _upgrade_hash_index_to_multiplexing_barcodes(value)


@upgrade_step('cell_line', '2', '3')
def cell_line_2_3(value, system):
    _upgrade_hash_index_to_multiplexing_barcodes(value)
