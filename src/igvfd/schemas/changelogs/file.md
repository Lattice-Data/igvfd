## Changelog for file.json

### Schema version 2

* Remove md5sum.

### Minor changes since schema version 2

* Update `aliases` regex to accept `shyam-prabhakar` prefix.
* Update `aliases` regex to accept `john-tsang` prefix.
* Update `aliases` regex to accept `silvia-domcke` prefix.
* Update `aliases` regex to accept `will-allen` prefix.
* Remove `file_size` comment.
* Update `crc64nvme_base64` comment.

### Minor changes since schema version 1

* Add `crc64nvme_base64` with Base64 format validation for AWS S3 CRC64NVME.
* Require `crc64nvme_base64` unless `no_file_available` is true (with `s3_uri`; see dependentSchemas).
* Add `s3_uri` with `s3://` prefix validation.
* Add `no_file_available` with default `false`.
* Require `s3_uri` unless `no_file_available` is true.
* Forbid `s3_uri` when `no_file_available` is true.

### Schema version 1

* Initial release
