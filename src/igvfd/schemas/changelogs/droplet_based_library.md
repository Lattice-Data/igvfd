# Droplet Based Library Changelog

### Schema version 2

* Merge *dependentSchemas* from abstract Library schema (including *multiplexing_method* requiring at least two samples).
* Remove *chemistry_version*.
* Remove *cell_barcode_length*.
* Remove *umi_length*.
* Adjust *multiplexing_method* enum list (inherited from abstract Library schema).

### Minor changes since schema version 1

* Add *library_cardinality* (inherited from abstract Library schema).
* Add *linked_libraries* (inherited from abstract Library schema; linkTo restricted to DropletBasedLibrary).
* Add `library_construction_technology` (inherited from abstract Library schema).

* Add `author_metadata` via `mixins.json#/author_metadata` (shared with abstract library profile).
* Move CRO_order to SequenceFileSet (inherited from Library).

## Schema version 1

* Initial release
* Concrete schema inheriting from abstract Library class
* Added droplet-based library-specific properties: chemistry_version, cell_barcode_length, umi_length, feature_types
