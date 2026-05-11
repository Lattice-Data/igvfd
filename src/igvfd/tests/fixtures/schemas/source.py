import pytest


@pytest.fixture
def source(testapp):
    item = {
        'name': 'pytest-fixture-vendor-sigma',
        'title': 'Sigma-Aldrich Fixture',
        'status': 'current',
    }
    return testapp.post_json('/source', item, status=201).json['@graph'][0]


@pytest.fixture
def source_with_url(testapp):
    item = {
        'name': 'pytest-fixture-vendor-abcam',
        'title': 'Abcam Fixture',
        'status': 'current',
        'url': 'https://www.abcam.com',
    }
    return testapp.post_json('/source', item, status=201).json['@graph'][0]
