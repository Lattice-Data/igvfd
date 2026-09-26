import json
import re

from .notes import append_upgrade_note


# The aliases pattern the steps calling preserve_invalid_aliases upgrade to, minus its
# prefix list. Stored aliases already passed the previous pattern, so their prefixes are
# known ones; these steps only enforce what that version narrowed: a single space between
# words and nothing after the last one. Leaving the prefixes out keeps routine prefix
# additions from touching the steps, which are historical once released, so do not edit
# this to track a later schema change. See test_upgrade_alias_pattern_agrees_with_schema.
ALIAS_PATTERN = re.compile(
    r"^[a-z0-9-]+:[a-zA-Z\d_$.+!*,()'-]+(?: [a-zA-Z\d_$.+!*,()'-]+)*(?![\s\S])"
)


def preserve_invalid_aliases(value):
    """Drop aliases the anchored pattern rejects, preserving them in notes.

    aliases has minItems 1, so the property is removed when no alias survives.
    """
    if not value.get('aliases'):
        return
    valid_aliases = []
    invalid_aliases = []
    for alias in value['aliases']:
        # search, matching how jsonschema applies `pattern`. The pattern ends with
        # `(?![\s\S])` rather than `$`, so search and fullmatch coincide.
        target = valid_aliases if ALIAS_PATTERN.search(alias) else invalid_aliases
        target.append(alias)
    if not invalid_aliases:
        return
    if valid_aliases:
        value['aliases'] = valid_aliases
    else:
        value.pop('aliases')
    # JSON-quote each alias: the whitespace that got it rejected is otherwise invisible.
    append_upgrade_note(
        value,
        'Aliases removed during schema upgrade: '
        f'{", ".join(json.dumps(alias) for alias in invalid_aliases)}.'
    )
