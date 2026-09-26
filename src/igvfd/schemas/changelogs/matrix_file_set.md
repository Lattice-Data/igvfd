## Changelog for matrix_file_set.json

### Schema version 3

* Update `aliases` regex to anchor at true end of input with `(?![\s\S])` rather than `$`.
* Update `aliases` regex to allow only single spaces between words.
* Preserve `aliases` rejected by the updated regex in `notes` during upgrade.

### Minor changes since schema version 2

* Update `aliases` regex to accept `shyam-prabhakar` prefix.
* Update `aliases` regex to accept `john-tsang` prefix.
* Update `aliases` regex to accept `silvia-domcke` prefix.
* Update `aliases` regex to accept `will-allen` prefix.
* Add *dbxrefs*, accepting GEO series, SRA study, and ENA study identifiers requiring at least one identifier when submitted, and anchored at true end of input.

### Schema version 2

* Remove experiment_ids.
* Remove source_sequence_file_sets.
* Remove software.
* Remove software_version.
* Remove genome_assembly.
* Remove genome_annotation.

### Schema version 1

* Initial release.
* Add experiment_ids as a required property.
