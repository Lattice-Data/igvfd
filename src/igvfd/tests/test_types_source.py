import pytest


def test_source_summary(testapp, source):
    res = testapp.get(source['@id'])
    assert res.json.get('summary') == 'Sigma-Aldrich'


def test_source_summary_matches_title(testapp):
    item = {
        'name': 'thermo-fisher',
        'title': 'Thermo Fisher Scientific',
    }
    source = testapp.post_json('/source', item, status=201).json['@graph'][0]
    res = testapp.get(source['@id'])
    assert res.json.get('summary') == 'Thermo Fisher Scientific'


def test_source_with_url(testapp, source_with_url):
    res = testapp.get(source_with_url['@id'])
    assert res.json.get('url') == 'https://www.abcam.com'
    assert res.json.get('summary') == 'Abcam'


def test_source_name_pattern_valid(testapp):
    item = {
        'name': 'valid-name-123',
        'title': 'Valid Source Name',
    }
    res = testapp.post_json('/source', item, status=201)
    assert res.json['@graph'][0]['name'] == 'valid-name-123'


def test_source_name_pattern_invalid(testapp):
    item = {
        'name': 'Invalid Name With Spaces',
        'title': 'Invalid Source',
    }
    testapp.post_json('/source', item, status=422)


def test_source_name_uppercase_invalid(testapp):
    item = {
        'name': 'UpperCase',
        'title': 'Upper Case Source',
    }
    testapp.post_json('/source', item, status=422)


def test_source_title_required(testapp):
    item = {
        'name': 'no-title-source',
    }
    testapp.post_json('/source', item, status=422)


def test_source_name_required(testapp):
    item = {
        'title': 'No Name Source',
    }
    testapp.post_json('/source', item, status=422)


def test_source_name_unique_key(testapp, source):
    item = {
        'name': 'sigma',
        'title': 'Sigma-Aldrich Duplicate',
    }
    testapp.post_json('/source', item, status=409)


def test_source_default_status(testapp):
    item = {
        'name': 'test-vendor',
        'title': 'Test Vendor',
    }
    res = testapp.post_json('/source', item, status=201)
    assert res.json['@graph'][0]['status'] == 'current'


def test_source_deleted_status(testapp):
    item = {
        'name': 'deleted-vendor',
        'title': 'Deleted Vendor',
        'status': 'deleted',
    }
    res = testapp.post_json('/source', item, status=201)
    assert res.json['@graph'][0]['status'] == 'deleted'
