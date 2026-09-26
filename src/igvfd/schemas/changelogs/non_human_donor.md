## Changelog for non_human_donor.json

### Schema version 3

* Update `aliases` regex to anchor at true end of input with `(?![\s\S])` rather than `$`.
* Update `aliases` regex to allow only single spaces between words.
* Update `aliases` regex to accept `shyam-prabhakar` prefix.
* Update `aliases` regex to accept `john-tsang` prefix.
* Update `aliases` regex to accept `silvia-domcke` prefix.
* Update `aliases` regex to accept `will-allen` prefix.
* Preserve `aliases` rejected by the updated regex in `notes` during upgrade.

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
