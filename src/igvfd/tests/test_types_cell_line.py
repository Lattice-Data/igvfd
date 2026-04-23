def test_cell_line_host_linkto_validation(testapp, other_lab, human_donor, controlled_term):
    testapp.post_json(
        '/cell_line',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term['@id']],
            'host': 'invalid-donor-id',
            'status': 'current',
        },
        status=422
    )


def test_cell_line_create_success(testapp, other_lab, human_donor, controlled_term):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/cell_line', item, status=201)
    assert res.json['@graph'][0]['lab'] == other_lab['@id']
    assert res.json['@graph'][0]['donors'] == [human_donor['@id']]
    assert res.json['@graph'][0]['sample_terms'] == [controlled_term['@id']]


def test_cell_line_create_with_all_optional_fields(
    testapp,
    other_lab,
    human_donor,
    controlled_term,
    non_human_donor
):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term['@id']],
        'host': non_human_donor['@id'],
        'host_tissue': controlled_term['@id'],
        'description': 'Test cell line with all fields',
        'status': 'current',
    }
    res = testapp.post_json('/cell_line', item, status=201)
    assert res.json['@graph'][0]['host'] == non_human_donor['@id']
    assert res.json['@graph'][0]['host_tissue'] == controlled_term['@id']
    assert res.json['@graph'][0]['description'] == 'Test cell line with all fields'


def test_cell_line_host_tissue_linkto_validation(testapp, other_lab, human_donor, controlled_term):
    testapp.post_json(
        '/cell_line',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term['@id']],
            'host_tissue': '/invalid/term/path/',
            'status': 'current',
        },
        status=422
    )


def test_cell_line_rejects_classification_field(testapp, other_lab, human_donor, controlled_term):
    testapp.post_json(
        '/cell_line',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term['@id']],
            'classification': 'immortalized cell line',
            'status': 'current',
        },
        status=422
    )
