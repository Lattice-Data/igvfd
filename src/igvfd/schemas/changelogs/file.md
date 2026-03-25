## Changelog for file.json

### Minor changes since schema version 1

* Add `s3_uri` with `s3://` prefix validation.
* Add `no_file_available` with default `false`.
* Require `s3_uri` unless `no_file_available` is true.
* Forbid `s3_uri` when `no_file_available` is true.

### Schema version 1

* Initial release
