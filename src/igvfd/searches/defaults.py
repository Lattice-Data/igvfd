OPTIONAL_PARAMS = [
    'datastore',
    'debug',
    'field',
    'format',
    'frame',
    'from',
    'limit',
    'mode',
    'sort',
    'type',
    'config',
]

FREE_TEXT_QUERIES = [
    'advancedQuery',
    'searchTerm',
    'query',
]

RESERVED_KEYS = NOT_FILTERS = OPTIONAL_PARAMS + FREE_TEXT_QUERIES

TOP_HITS_ITEM_TYPES = [
    'Document',
    'Image',
    'Lab',
    'Page',
    'User'
]

DEFAULT_ITEM_TYPES = TOP_HITS_ITEM_TYPES

# Top_hits_item_types interact with the search box
# Default item types would be searchable using ?searchTerm=ABC format in the url without having to use &type=Item
