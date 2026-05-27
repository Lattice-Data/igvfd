## Changelog for raw_matrix_file.json

### Schema version 4

* Add software.
* Add software_version.
* Add genome_assembly.

### Schema version 3

* Remove md5sum.

### Minor changes since schema version 2

* Remove duplicate `matrix_file_sets` definition from the JSON profile.
* Update `matrix_file_sets` calculated property schema metadata on the type class.
* Extend `feature_keys` enum list to include "crispr guide ID".
* Extend `feature_keys` enum list to include "hash oligo".
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
