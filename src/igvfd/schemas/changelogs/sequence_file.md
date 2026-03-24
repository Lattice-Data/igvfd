## Changelog for sequence_file.json

### Schema version 2

* Add `read_count` (from file mixin).
* Require `read_count` when `no_file_available` is not true (`read_count_when_file_available` in `dependentSchemas`).

### Minor changes since schema version 1

* Require `s3_uri` unless `no_file_available` is true.
* Forbid `s3_uri` when `no_file_available` is true.

### Schema version 1

* Initial release
