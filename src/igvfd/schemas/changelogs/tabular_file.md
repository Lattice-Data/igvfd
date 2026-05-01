## Changelog for tabular_file.json

### Minor changes since schema version 2

### Schema version 2

* Bump schema version for inherited `crc64nvme_base64` requirement from file profile when file is available.

### Minor changes since schema version 1

* Require `s3_uri` unless `no_file_available` is true.
* Forbid `s3_uri` when `no_file_available` is true.

### Schema version 1

* Initial release
