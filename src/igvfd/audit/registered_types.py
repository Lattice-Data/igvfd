import venusian

from snovault.interfaces import (
    AUDITOR,
)


class _RecordingConfig:
    """Stands in for a pyramid Configurator so that a venusian scan can be
    captured without building an app, a registry, or a database connection.

    ``audit_checker`` only attaches a venusian callback whose body calls
    ``scanner.config.add_audit_checker(...)``, so recording that call gives
    exactly what the running app registers.
    """

    def __init__(self):
        self.records = []

    def add_audit_checker(self, checker, type_, condition=None, frame='embedded'):
        self.records.append((checker, type_))


def _dispatched_functions(checker):
    """Yield the audit functions that a registered checker delegates to.

    Dispatchers iterate a module level ``function_dispatcher_*`` dict, so find
    that dict by walking the names the dispatcher body references. A checker
    registered directly, without such a dict, is its own audit function.
    """
    for name in checker.__code__.co_names:
        candidate = checker.__globals__.get(name)
        if isinstance(candidate, dict) and candidate and all(callable(value) for value in candidate.values()):
            yield from candidate.values()
            return
    yield checker


def get_types_by_audit_function(package):
    """Map ``module.function`` to the sorted @types it is registered against.

    The @type names come from ``TypeInfo.name``, which is the item class name,
    so they match the type names in the ``_hierarchy`` of ``/profiles``.
    """
    config = _RecordingConfig()
    venusian.Scanner(config=config).scan(package, categories=(AUDITOR,))
    types_by_function = {}
    for checker, type_ in config.records:
        for function in _dispatched_functions(checker):
            full_name = f'{function.__module__}.{function.__name__}'
            types_by_function.setdefault(full_name, set()).add(type_)
    return {
        full_name: sorted(types)
        for full_name, types in types_by_function.items()
    }
