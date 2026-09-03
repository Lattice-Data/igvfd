# Plate Based Library Changelog

### Schema version 6

* Update inherited *dbxrefs* regex to accept Biomaterial-prefixed BioSample sample identifiers (SAME, SAMN, SAMD, each optionally followed by A or G) and EGA sample identifiers (EGAN), alongside SRS and ERS sample identifiers and GSM, SRX, ERX, and EGAX experiment identifiers, while excluding obsolete GEO identifiers.
* Require at least one dbxref when inherited *dbxrefs* is submitted.
* Preserve *dbxrefs* rejected by the updated regex in *notes* during upgrade.

### Schema version 5

* Remove requirement for at least two samples when *multiplexing_method* is present (inherited from abstract Library schema).

### Schema version 4

* Require *feature_types* (inherited from abstract Library schema).

### Minor changes since schema version 3

* Extend *feature_types* enum list to include *CRISPR Guide Capture* (inherited from abstract Library schema).

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

* Add `library_construction_technology` (inherited from abstract Library schema).

* Add `author_metadata` via `mixins.json#/author_metadata` (shared with abstract library profile).
* Move CRO_order to SequenceFileSet (inherited from Library).

## Schema version 1

* Initial release
* Concrete schema inheriting from abstract Library class
* Added plate-based library-specific properties: kit_version, indexing_rounds
