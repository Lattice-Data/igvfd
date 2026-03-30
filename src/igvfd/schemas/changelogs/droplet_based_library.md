# Droplet Based Library Changelog

* Add `author_metadata` via `mixins.json#/author_metadata` (shared with abstract library profile).
* Move CRO_order to SequenceFileSet (inherited from Library).

## Schema version 1

* Initial release
* Concrete schema inheriting from abstract Library class
* Added droplet-based library-specific properties: chemistry_version, cell_barcode_length, umi_length, feature_types
