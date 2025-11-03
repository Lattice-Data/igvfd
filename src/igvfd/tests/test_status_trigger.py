import pytest


items = [
    {'description': 'item0'},
    {'description': 'item1'},
    {'description': 'item2'},
]


@pytest.fixture
def content(testapp):
    url = '/test-igvf-items/'
    for item in items:
        testapp.post_json(url, item)


def test_item_set_status_method_exists(testapp, content, root):
    res = testapp.get('/test-igvf-items/')
    igvf_item_uuid = res.json['@graph'][0]['uuid']
    igvf_item = root.get_by_uuid(igvf_item_uuid)
    set_status_method = getattr(igvf_item, 'set_status', None)
    assert callable(set_status_method)


def test_item_set_status_up_down_lists_exists(testapp, content, root):
    res = testapp.get('/test-igvf-items/')
    igvf_item_uuid = res.json['@graph'][0]['uuid']
    igvf_item = root.get_by_uuid(igvf_item_uuid)
    assert hasattr(igvf_item, 'set_status_up')
    assert hasattr(igvf_item, 'set_status_down')
    assert isinstance(igvf_item.set_status_up, list)
    assert isinstance(igvf_item.set_status_down, list)


def test_item_set_status_no_status_validation_error(testapp, content, root):
    res = testapp.get('/test-igvf-items/')
    igvf_item_uuid = res.json['@graph'][0]['uuid']
    igvf_item_id = res.json['@graph'][0]['@id']
    igvf_item = root.get_by_uuid(igvf_item_uuid)
    igvf_item_properties = igvf_item.properties
    igvf_item_properties.pop('status')
    igvf_item.update(igvf_item_properties)
    res = testapp.get(igvf_item_id)
    assert 'status' not in res.json
    res = testapp.patch_json(igvf_item_id + '@@set_status', {'status': 'current'}, status=422)
    assert res.json['errors'][0]['description'] == 'No property status'


def test_item_current_endpoint_calls_set_status(testapp, content, mocker):
    from igvfd.types.base import Item
    res = testapp.get('/test-igvf-items/')
    igvf_item_id = res.json['@graph'][0]['@id']
    mocker.patch('igvfd.types.base.Item.set_status')
    testapp.patch_json(igvf_item_id + '@@set_status', {'status': 'current'})
    assert Item.set_status.call_count == 1


def test_item_current_endpoint_triggers_set_status(testapp, content, mocker):
    from igvfd.types.base import Item
    res = testapp.get('/test-igvf-items/')
    igvf_item_id = res.json['@graph'][0]['@id']
    mocker.spy(Item, 'set_status')
    testapp.patch_json(igvf_item_id + '@@set_status', {'status': 'current'})
    assert Item.set_status.call_count == 1


def test_set_status_endpoint_status_not_specified(testapp, content):
    res = testapp.get('/test-igvf-items/')
    igvf_item_id = res.json['@graph'][0]['@id']
    res = testapp.patch_json(igvf_item_id + '@@set_status?update=true', {}, status=422)
    assert res.json['errors'][0]['description'] == 'Status not specified'


def test_set_status_endpoint_status_specified(testapp, content):
    res = testapp.get('/test-igvf-items/')
    igvf_item_id = res.json['@graph'][0]['@id']
    testapp.patch_json(
        igvf_item_id + '@@set_status?update=true&force_audit=true',
        {'status': 'current'},
        status=200
    )


def test_item_set_status_current_deleted_transitions(testapp, content, root, dummy_request):
    res = testapp.get('/test-igvf-items/')
    igvf_item_id = res.json['@graph'][0]['@id']
    # Item starts with 'current' (default from schema)
    res = testapp.get(igvf_item_id)
    assert res.json['status'] == 'current'

    # Test: current -> deleted (valid transition)
    testapp.patch_json(igvf_item_id + '@@set_status?update=true', {'status': 'deleted'}, status=200)
    res = testapp.get(igvf_item_id)
    assert res.json['status'] == 'deleted'

    # Test: deleted -> current (valid transition, allowed per STATUS_TRANSITION_TABLE)
    testapp.patch_json(igvf_item_id + '@@set_status?update=true', {'status': 'current'}, status=200)
    res = testapp.get(igvf_item_id)
    assert res.json['status'] == 'current'

    # Test: current -> current (same status, should work)
    testapp.patch_json(igvf_item_id + '@@set_status?update=true', {'status': 'current'}, status=200)
    res = testapp.get(igvf_item_id)
    assert res.json['status'] == 'current'
