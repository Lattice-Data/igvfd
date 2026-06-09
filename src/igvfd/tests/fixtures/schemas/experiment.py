import pytest


@pytest.fixture
def experiment(testapp, other_lab, droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'libraries': [droplet_based_library['@id']],
        'status': 'current',
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_with_aliases(testapp, other_lab, droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'libraries': [droplet_based_library['@id']],
        'aliases': ['lattice:pytest-experiment-basic'],
        'status': 'current',
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_with_description(testapp, other_lab, droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'libraries': [droplet_based_library['@id']],
        'description': 'Test experiment grouping droplet libraries',
        'status': 'current',
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_with_cro_identifier(testapp, other_lab, droplet_based_library):
    item = {
        'lab': other_lab['@id'],
        'libraries': [droplet_based_library['@id']],
        'CRO_experiment_identifier': 'CRO-EXP-2024-01',
        'status': 'current',
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_plate_only(testapp, other_lab, plate_based_library):
    item = {
        'lab': other_lab['@id'],
        'libraries': [plate_based_library['@id']],
        'status': 'current',
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_mixed_libraries(testapp, other_lab, droplet_based_library, plate_based_library):
    item = {
        'lab': other_lab['@id'],
        'libraries': [
            droplet_based_library['@id'],
            plate_based_library['@id'],
        ],
        'status': 'current',
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]
