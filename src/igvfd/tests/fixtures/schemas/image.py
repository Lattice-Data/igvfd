import pytest
from ...constants import *


@pytest.fixture
def image(testapp):
    item = {
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT},
        'status': 'current'
    }
    return testapp.post_json('/image', item, status=201).json['@graph'][0]
