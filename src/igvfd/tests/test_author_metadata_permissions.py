import pytest
from webtest import TestApp as WebTestApp


def _remote_user_testapp(app, remote_user):
    return WebTestApp(
        app,
        {
            'HTTP_ACCEPT': 'application/json',
            'REMOTE_USER': str(remote_user),
        },
    )


@pytest.fixture
def lab_submitter_testapp(submitter, app, external_tx, zsa_savepoints):
    return _remote_user_testapp(app, submitter['uuid'])


@pytest.fixture
def group_submitter_testapp(app):
    return WebTestApp(
        app,
        {
            'HTTP_ACCEPT': 'application/json',
            'REMOTE_USER': 'TEST_SUBMITTER',
        },
    )


@pytest.fixture
def wrangler_remote_testapp(wrangler, app, external_tx, zsa_savepoints):
    return _remote_user_testapp(app, wrangler['uuid'])


def _human_donor_item(lab_id, **extra):
    item = {
        'lab': lab_id,
        'taxa': 'Homo sapiens',
        'status': 'current',
    }
    item.update(extra)
    return item


def test_admin_post_human_donor_with_author_metadata(testapp, other_lab):
    item = _human_donor_item(
        other_lab['@id'],
        author_metadata={'external_subject_id': 'ADM-1'},
    )
    res = testapp.post_json('/human_donor', item, status=201)
    assert res.json['@graph'][0]['author_metadata'] == item['author_metadata']


def test_lab_submitter_post_human_donor_with_author_metadata_rejected(lab_submitter_testapp, lab):
    item = _human_donor_item(
        lab['@id'],
        author_metadata={'external_subject_id': 'SUB-1'},
    )
    lab_submitter_testapp.post_json('/human_donor', item, status=422)


def test_group_submitter_post_human_donor_with_author_metadata_rejected(
    group_submitter_testapp, other_lab
):
    item = _human_donor_item(
        other_lab['@id'],
        author_metadata={'external_subject_id': 'GRP-1'},
    )
    group_submitter_testapp.post_json('/human_donor', item, status=422)


def test_lab_submitter_patch_human_donor_author_metadata_rejected(
    testapp, lab_submitter_testapp, lab
):
    res = testapp.post_json(
        '/human_donor',
        _human_donor_item(lab['@id']),
        status=201,
    )
    url = res.json['@graph'][0]['@id']
    lab_submitter_testapp.patch_json(
        url,
        {'author_metadata': {'patched_by_submitter': True}},
        status=422,
    )


def test_wrangler_patch_human_donor_author_metadata_allowed(
    testapp, wrangler_remote_testapp, lab
):
    res = testapp.post_json(
        '/human_donor',
        _human_donor_item(lab['@id']),
        status=201,
    )
    url = res.json['@graph'][0]['@id']
    meta = {'wrangler_set': True, 'batch': 'B1'}
    wrangler_remote_testapp.patch_json(url, {'author_metadata': meta}, status=200)
    got = wrangler_remote_testapp.get(url).json
    assert got['author_metadata'] == meta
