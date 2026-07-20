# Library Changelog

### Minor changes since schema version 1

* Add *library_cardinality*.
* Add *linked_libraries*.
* Require dual cardinality when *linked_libraries* is present.
* Adjust *multiplexing_method* to be an array with a single value and extend enum list to include *antibody hashing*.
* Adjust *multiplexing_method* to be an array with a single value and extend enum list to include *lipid hashing*.
* Adjust *multiplexing_method* to be an array with a single value and extend enum list to include *chemical hashing*.
* Adjust *multiplexing_method* to be an array with a single value and extend enum list to include *probe barcoding*.
* Adjust *multiplexing_method* to be an array with a single value and extend enum list to include *natural genetic variation*.
* Adjust *multiplexing_method* to be an array with a single value and extend enum list to include *combinatorial indexing*.
* Reduce *multiplexing_method* enum list to exclude *cell hashing*.
* Reduce *multiplexing_method* enum list to exclude *genetic*.
* Reduce *multiplexing_method* enum list to exclude *sample barcodes*.
* Add *feature_types*.
* Update *CRO_group_identifier* description.

- Add optional `dbxrefs` for external library identifiers (EGA, GEO, SRA, ENA).
* Add `library_construction_technology`.

- Add `CRO_group_identifier`.
- Remove `author_metadata` from abstract library profile; concrete library types use `mixins.json#/author_metadata`.
- Move CRO_order to SequenceFileSet.
- Initial abstract schema definition.
