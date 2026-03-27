## Changelog for sequence_file.json

### Schema version 2

* Add `read_count` as a sequence-file-only property.
* Require `read_count` when `no_file_available` is `false` (`dependentSchemas.no_file_available`).

### Minor changes since schema version 1

* Require `s3_uri` unless `no_file_available` is true.
* Forbid `s3_uri` when `no_file_available` is true.

### Schema version 1

* Initial release
