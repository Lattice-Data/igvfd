## Changelog for sequence_file.json

### Schema version 4

* Remove md5sum.

### Minor changes since schema version 3

* Remove duplicate `sequence_file_sets` definition from the JSON profile; calculated property unchanged on the type class.

### Schema version 3

* Bump schema version for inherited `crc64nvme_base64` requirement from file profile when file is available.

### Minor changes since schema version 2

* Add calculated property `sequence_file_sets`.

### Schema version 2

* Add `read_count` as a sequence-file-only property.
* Require `read_count` when `no_file_available` is `false` (`dependentSchemas.no_file_available`).

### Minor changes since schema version 1

* Require `s3_uri` unless `no_file_available` is true.
* Forbid `s3_uri` when `no_file_available` is true.

### Schema version 1

* Initial release
