# Controlled Term Changelog

### Minor changes since schema version 2

* Update dbxrefs regex to accept CAS Registry Numbers.

### Schema version 2

* Remove `term_name` from stored properties; `term_name` is a calculated property only.

### Minor changes since schema version 1

* Update description to remove reference to experimental conditions.
* Add term_id as identifying property.

- Initial schema definition for controlled vocabulary terms from biological ontologies.
- Added support for `HANCESTRO` as a valid `ontology_source` and `term_id` prefix.
