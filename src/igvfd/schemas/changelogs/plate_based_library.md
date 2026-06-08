# Plate Based Library Changelog

### Schema version 2

* Merge *dependentSchemas* from abstract Library schema (including *multiplexing_method* requiring at least two samples).
* Remove *kit_version*.
* Remove *indexing_rounds*.
* Add *feature_types* (inherited from abstract Library schema).
* Adjust *multiplexing_method* enum list (inherited from abstract Library schema).

### Minor changes since schema version 1

* Add `library_construction_technology` (inherited from abstract Library schema).

* Add `author_metadata` via `mixins.json#/author_metadata` (shared with abstract library profile).
* Move CRO_order to SequenceFileSet (inherited from Library).

## Schema version 1

* Initial release
* Concrete schema inheriting from abstract Library class
* Added plate-based library-specific properties: kit_version, indexing_rounds
