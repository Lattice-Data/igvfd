# Primary Cell Culture Changelog

## Schema version 3

* Rename hash_index to multiplexing_barcodes.

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
* Merge dependentSchemas from biosample.json via `$merge`.
* Require lower_bound_age, upper_bound_age, and age_units together when any one is submitted (from biosample dependentSchemas).

## Schema version 1

* Initial release
* Concrete schema inheriting from abstract Biosample class
* Added primary cell culture-specific properties: passage_number, date_obtained
