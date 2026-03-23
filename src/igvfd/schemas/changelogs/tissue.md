# Tissue Changelog

## Minor changes since schema version 1

* Add lower_bound_age.
* Add upper_bound_age.
* Add age_units.
* Merge dependentSchemas from biosample.json and mixins.json tissue thickness rules via `$merge`.
* Require lower_bound_age, upper_bound_age, and age_units together when any one is submitted (from biosample dependentSchemas).

## Schema version 1

* Initial release
* Concrete schema inheriting from abstract Biosample class
* Added tissue-specific properties: spatial_information, preservation_method, thickness, thickness_units, date_obtained, orientation
