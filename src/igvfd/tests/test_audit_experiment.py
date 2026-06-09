from igvfd.audit.experiment import (
    audit_experiment_mixed_library_types,
)


def test_experiment_all_droplet_libraries_no_audit():
    value = {
        '@type': ['Experiment'],
        '@id': '/experiments/IGVFDTEST0001/',
        'libraries': [
            {
                '@id': '/droplet-based-libraries/IGVFDTEST0001/',
                '@type': ['DropletBasedLibrary', 'Library', 'Item'],
            },
            {
                '@id': '/droplet-based-libraries/IGVFDTEST0002/',
                '@type': ['DropletBasedLibrary', 'Library', 'Item'],
            },
        ],
    }
    failures = list(audit_experiment_mixed_library_types(value, {}))
    assert len(failures) == 0


def test_experiment_all_plate_libraries_no_audit():
    value = {
        '@type': ['Experiment'],
        '@id': '/experiments/IGVFDTEST0001/',
        'libraries': [
            {
                '@id': '/plate-based-libraries/IGVFDTEST0001/',
                '@type': ['PlateBasedLibrary', 'Library', 'Item'],
            },
        ],
    }
    failures = list(audit_experiment_mixed_library_types(value, {}))
    assert len(failures) == 0


def test_experiment_mixed_library_types_audit():
    value = {
        '@type': ['Experiment'],
        '@id': '/experiments/IGVFDTEST0001/',
        'libraries': [
            {
                '@id': '/droplet-based-libraries/IGVFDTEST0001/',
                '@type': ['DropletBasedLibrary', 'Library', 'Item'],
            },
            {
                '@id': '/plate-based-libraries/IGVFDTEST0001/',
                '@type': ['PlateBasedLibrary', 'Library', 'Item'],
            },
        ],
    }
    failures = list(audit_experiment_mixed_library_types(value, {}))
    assert len(failures) == 1
    assert failures[0].category == 'inconsistent library types'


def test_experiment_no_libraries_no_audit():
    value = {
        '@type': ['Experiment'],
        '@id': '/experiments/IGVFDTEST0001/',
        'libraries': [],
    }
    failures = list(audit_experiment_mixed_library_types(value, {}))
    assert len(failures) == 0
