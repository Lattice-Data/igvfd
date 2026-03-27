# Primary Cell Culture Changelog

## Minor changes since schema version 1

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
