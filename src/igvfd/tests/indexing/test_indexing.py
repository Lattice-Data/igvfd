import pytest

import time


pytestmark = [pytest.mark.indexing]


def test_indexing_simple_igvfd(testapp, workbook, poll_until_indexing_is_done):
    response = testapp.post_json('/testing-post-put-patch/', {'required': ''})
    response = testapp.post_json('/testing-post-put-patch/', {'required': ''})
    poll_until_indexing_is_done(testapp)
    response = testapp.get('/search/?type=TestingPostPutPatch')
    assert len(response.json['@graph']) == 2


def test_indexing_updated_name_invalidates_dependents(testapp, dummy_request, workbook, poll_until_indexing_is_done):
    response = testapp.get('/search/?type=User&lab=/labs/teri-klein/')
    assert len(response.json['@graph']) >= 7
    testapp.patch_json(
        '/labs/teri-klein/',
        {'name': 'some-other-name'}
    )
    poll_until_indexing_is_done(testapp)
    response = testapp.get('/search/?type=User&lab=/labs/some-other-name/')
    assert len(response.json['@graph']) >= 7
    testapp.get('/search/?type=User&lab=/labs/teri-klein/', status=404)
    testapp.patch_json(
        '/labs/some-other-name/',
        {'name': 'teri-klien'}
    )
    poll_until_indexing_is_done(testapp)
    testapp.get('/search/?type=User&lab=/labs/some-other-lab/', status=404)
    response = testapp.get('/search/?type=User&lab=/labs/teri-klein/')
    assert len(response.json['@graph']) >= 7
