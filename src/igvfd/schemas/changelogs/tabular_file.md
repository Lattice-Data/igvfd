## Changelog for tabular_file.json

### Minor changes since schema version 6

* Make the inherited `s3_uri` immutable with `requestMethod: POST`: it is set when the file is created, and a PATCH or PUT that changes it, or adds it to a file that has none, is rejected. Resending the stored value is still accepted.
* Anchor the inherited `crc64nvme_base64` pattern at the true end of input with `(?![\s\S])` rather than `$`, so a value with a trailing newline is rejected.

### Schema version 6

* Update `aliases` regex to anchor at true end of input with `(?![\s\S])` rather than `$`.
* Update `aliases` regex to allow only single spaces between words.
* Update `aliases` regex to accept `shyam-prabhakar` prefix.
* Update `aliases` regex to accept `john-tsang` prefix.
* Update `aliases` regex to accept `silvia-domcke` prefix.
* Update `aliases` regex to accept `will-allen` prefix.
* Preserve `aliases` rejected by the updated regex in `notes` during upgrade.

### Schema version 5

* Add `guides_signature`.
* Require `guides_signature` when `content_type` is `guide RNA sequences`.
* Require `guides_signature` to be unique across the portal.

### Schema version 4

* Add `content_type`.
* Require `content_type`.

### Schema version 3

* Remove md5sum.

### Minor changes since schema version 3

* Update inherited `file_size` and `crc64nvme_base64` comments from file profile.

### Minor changes since schema version 2

### Schema version 2

* Bump schema version for inherited `crc64nvme_base64` requirement from file profile when file is available.

### Minor changes since schema version 1

* Require `s3_uri` unless `no_file_available` is true.
* Forbid `s3_uri` when `no_file_available` is true.

### Schema version 1

* Initial release
