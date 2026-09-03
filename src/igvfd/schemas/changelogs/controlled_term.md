# Controlled Term Changelog

### Schema version 3

* Anchor *dbxrefs* at true end of input with `(?![\s\S])` rather than `$`, rejecting trailing whitespace consistently across regex dialects.
* Require at least one dbxref when *dbxrefs* is submitted.
* Preserve *dbxrefs* rejected by the updated regex in *notes* during upgrade.

### Minor changes since schema version 2

* Extend ontology_source enum list to include ZFS.
* Update term_id regex to accept ZFS prefix.
* Update dbxrefs regex to accept CAS Registry Numbers.

### Schema version 2

* Remove `term_name` from stored properties; `term_name` is a calculated property only.

### Minor changes since schema version 1

* Update description to remove reference to experimental conditions.
* Add term_id as identifying property.

- Initial schema definition for controlled vocabulary terms from biological ontologies.
- Added support for `HANCESTRO` as a valid `ontology_source` and `term_id` prefix.
