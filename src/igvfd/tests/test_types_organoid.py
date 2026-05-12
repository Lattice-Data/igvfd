def test_organoid_create_success(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/organoid', item, status=201)
    assert res.json['@graph'][0]['lab'] == other_lab['@id']
    assert res.json['@graph'][0]['donors'] == [human_donor['@id']]
    assert res.json['@graph'][0]['sample_terms'] == [controlled_term_brain['@id']]


def test_organoid_create_with_all_optional_fields(testapp, other_lab, human_donor, controlled_term_brain):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'description': 'Test organoid with all fields',
        'status': 'current',
    }
    res = testapp.post_json('/organoid', item, status=201)
    assert res.json['@graph'][0]['description'] == 'Test organoid with all fields'


def test_organoid_create_with_intended_cell_types(testapp, other_lab, human_donor, controlled_term_brain, controlled_term):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'intended_cell_types': [controlled_term['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/organoid', item, status=201)
    assert res.json['@graph'][0]['intended_cell_types'] == [controlled_term['@id']]


def test_organoid_create_with_origin_cell_types(testapp, other_lab, human_donor, controlled_term_brain, controlled_term):
    item = {
        'lab': other_lab['@id'],
        'donors': [human_donor['@id']],
        'sample_terms': [controlled_term_brain['@id']],
        'origin_cell_types': [controlled_term['@id']],
        'status': 'current',
    }
    res = testapp.post_json('/organoid', item, status=201)
    assert res.json['@graph'][0]['origin_cell_types'] == [controlled_term['@id']]


def test_organoid_rejects_classification_field(testapp, other_lab, human_donor, controlled_term_brain):
    testapp.post_json(
        '/organoid',
        {
            'lab': other_lab['@id'],
            'donors': [human_donor['@id']],
            'sample_terms': [controlled_term_brain['@id']],
            'classification': 'organoid',
            'status': 'current',
        },
        status=422
    )
