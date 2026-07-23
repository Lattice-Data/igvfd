# Plate Based Library Changelog

### Schema version 3

* Add *library_cardinality* (required; inherited from abstract Library schema).
* Add *linked_libraries* (inherited from abstract Library schema; linkTo restricted to PlateBasedLibrary).

### Schema version 2

* Merge *dependentSchemas* from abstract Library schema (including *multiplexing_method* requiring at least two samples).
* Remove *kit_version*.
* Remove *indexing_rounds*.
* Add *feature_types* (inherited from abstract Library schema).
* Adjust *multiplexing_method* enum list (inherited from abstract Library schema).

### Minor changes since schema version 1

* Add *guide_rna_files* (inherited from abstract Library schema).
* Extend *feature_types* enum list to include *CRISPR Guide Capture* (inherited from abstract Library schema).
* Require *feature_types* to include *CRISPR Guide Capture* when *guide_rna_files* is submitted (inherited from abstract Library schema).
* Add `library_construction_technology` (inherited from abstract Library schema).

* Add `author_metadata` via `mixins.json#/author_metadata` (shared with abstract library profile).
* Move CRO_order to SequenceFileSet (inherited from Library).

## Schema version 1

* Initial release
* Concrete schema inheriting from abstract Library class
* Added plate-based library-specific properties: kit_version, indexing_rounds
