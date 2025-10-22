import pytest
from ...constants import *


@pytest.fixture
def image(testapp):
    item = {
        'attachment': 'red-dot.png',
        'caption': 'A red dot image for testing.',
        'schema_version': '1',
        'status': 'current'
    }
    return testapp.post_json('/image', item, status=201).json['@graph'][0]
