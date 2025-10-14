import pytest
from snovault.elasticsearch.searches.interfaces import SEARCH_CONFIG
from snovault import TYPES


def test_search_config_items_columns(registry):
    item_registry = registry[TYPES]
    search_registry = registry[SEARCH_CONFIG]
    subtypes = item_registry.abstract['Item'].subtypes
    item_columns = search_registry.get('Item').columns
    subtypes_configs = search_registry.get_configs_by_names(subtypes)
    for config in subtypes_configs:
        for column in config.columns:
            assert column in item_columns
