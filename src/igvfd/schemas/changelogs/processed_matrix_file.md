## Changelog for processed_matrix_file.json

### Minor changes since schema version 5

* Add optional `md5sum`, a lowercase hex MD5 of the file content, not allowed when `no_file_available` is true. This is not the `md5sum` removed in schema version 3: it is optional, and missing values are flagged by an ERROR audit rather than rejected.
* Anchor the inherited `crc64nvme_base64` pattern at the true end of input with `(?![\s\S])` rather than `$`, so a value with a trailing newline is rejected.

### Schema version 5

* Update `aliases` regex to anchor at true end of input with `(?![\s\S])` rather than `$`.
* Update `aliases` regex to allow only single spaces between words.
* Update `aliases` regex to accept `shyam-prabhakar` prefix.
* Update `aliases` regex to accept `john-tsang` prefix.
* Update `aliases` regex to accept `silvia-domcke` prefix.
* Update `aliases` regex to accept `will-allen` prefix.
* Preserve `aliases` rejected by the updated regex in `notes` during upgrade.

### Schema version 4

* Add `is_multiplexed`.

### Minor changes since schema version 4

* Define `feature_counts` `feature_type` enum list on the processed matrix file profile.
* Update inherited `file_size` and `crc64nvme_base64` comments from file profile.

### Schema version 3

* Remove md5sum.

### Minor changes since schema version 2

* Remove duplicate `matrix_file_sets` definition from the JSON profile.
* Update `matrix_file_sets` calculated property schema metadata on the type class.
* Extend `feature_counts` `feature_type` enum list to include "guide capture".
* Add `samples`.

### Schema version 2

* Bump schema version for inherited `crc64nvme_base64` requirement from file profile when file is available.

### Minor changes since schema version 1

* Add calculated property `matrix_file_sets`.
* Add shared matrix metadata fields via `mixins.json#/matrix_shared`.
* Add `feature_keys`.
* Add `observation_count`.
* Add `feature_counts`.

### Schema version 1

* Initial release
