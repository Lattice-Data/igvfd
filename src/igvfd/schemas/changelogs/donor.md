# Donor Changelog

- Change `taxa` to a link to a ControlledTerm.
- Update `aliases` regex to anchor at true end of input with `(?![\s\S])` rather than `$`.
- Update `aliases` regex to allow only single spaces between words.
- Update `aliases` regex to accept `shyam-prabhakar` prefix.
- Update `aliases` regex to accept `john-tsang` prefix.
- Update `aliases` regex to accept `silvia-domcke` prefix.
- Update `aliases` regex to accept `will-allen` prefix.
- Add `cxg_donor_id`.
- Remove `author_metadata` from abstract donor profile; concrete donor types use `mixins.json#/author_metadata`.
- Add sex.
- Initial abstract schema definition.
