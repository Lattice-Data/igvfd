# Tissue Changelog

## Schema version 4

* Remove inherited dbxrefs.
* Preserve removed dbxrefs in notes during upgrade.

## Schema version 3

* Rename hash_index to multiplexing_barcodes.

## Minor changes since schema version 3

* Extend orientation enum list to include perpendicular.
* Use inherited `preservation_method` from abstract biosample profile.
* Update multiplexing_barcodes regex to allow a paired 10x Flex probe and CRISPR Flex barcode, such as BC001+CR001.
* Add RT_indexes.
* Add calculated property `libraries`.

## Minor changes since schema version 2

* Add developmental_stages.

## Schema version 2

* Bump schema_version default to 2.
* Inherit selection_kits from abstract biosample profile.
* Inherit selection_methods from abstract biosample profile.
* Inherit selection_markers from abstract biosample profile.
* Remove inherited enrichment_method.
* Remove inherited enrichment_markers.

## Minor changes since schema version 1

* Use inherited `date_obtained` from abstract biosample profile.
* Use inherited `collection_geographical_location` from abstract biosample profile.
* Add `author_metadata` via `mixins.json#/author_metadata` (shared with abstract biosample profile).
* Add lower_bound_age.
* Add upper_bound_age.
* Add age_units.
* Merge dependentSchemas from biosample.json and mixins.json tissue thickness rules via `$merge`.
* Require lower_bound_age, upper_bound_age, and age_units together when any one is submitted (from biosample dependentSchemas).

## Schema version 1

* Initial release
* Concrete schema inheriting from abstract Biosample class
* Added tissue-specific properties: spatial_information, preservation_method, thickness, thickness_units, date_obtained, orientation
