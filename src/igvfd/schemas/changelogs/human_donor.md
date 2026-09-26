# Human Donor Changelog

### Schema version 3

* Update `aliases` regex to anchor at true end of input with `(?![\s\S])` rather than `$`.
* Update `aliases` regex to allow only single spaces between words.
* Update `aliases` regex to accept `shyam-prabhakar` prefix.
* Update `aliases` regex to accept `john-tsang` prefix.
* Update `aliases` regex to accept `silvia-domcke` prefix.
* Update `aliases` regex to accept `will-allen` prefix.
* Preserve `aliases` rejected by the updated regex in `notes` during upgrade.

### Schema version 2

- Require cxg_donor_id.
- Update cxg_donor_id regex to reject placeholder whole-string values na, n/a, n\.a., null, unknown, unspecified, none, tbd, not applicable while requiring substantive non-whitespace text.

### Schema version 1

- Add `author_metadata` via `mixins.json#/author_metadata` (shared with abstract donor profile).
- Sort sex enum list lexicographically.
- Initial schema definition for human research subjects and donors.
- Added `sex` field with allowed values: male, female, unspecified, mixed (default: unspecified).
