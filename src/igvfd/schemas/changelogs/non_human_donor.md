## Changelog for non_human_donor.json

### Schema version 2

* Require cxg_donor_id.
* Update cxg_donor_id regex to reject placeholder whole-string values na, n/a, n\.a., null, unknown, unspecified, none, tbd, not applicable while requiring substantive non-whitespace text.

### Minor changes since schema version 1

* Add `author_metadata` via `mixins.json#/author_metadata` (shared with abstract donor profile).
* Add sex with taxa-dependent validation via dependentSchemas.
* Extend taxa enum list to include Danio rerio.
* Sort taxa enum list lexicographically.

### Schema version 1

- Initial release defining non human donor schema derived from donor.json with a taxa enumeration.
