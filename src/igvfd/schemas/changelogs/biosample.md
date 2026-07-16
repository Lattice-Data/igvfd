# Biosample Changelog

## Schema version 3

* Rename hash_index to multiplexing_barcodes.

## Minor changes since schema version 3

* Add RT_indexes.
* Add calculated property `libraries`.

## Minor changes since schema version 2

* Add developmental_stages.

## Schema version 2

* Add optional `dbxrefs` for external biosample identifiers (EGA, BioSample, SRA, ENA).
* Remove igvf_utils from submissionExample for selection_kits, selection_methods, and sources.
* Adjust selection_kits enum list to use ASCII-friendly strings (EasySep without trademark symbol; Naive without diacritic).
* Remove enrichment_method.
* Remove enrichment_markers.
* Add selection_kits.
* Add selection_methods.
* Add selection_markers.
* Update enriched_cell_types description.
* Update depleted_cell_types description.

During upgrade from schema version 1, enrichment_markers expression_level values low and high map to CD{n}+ alongside positive and intermediate.

## Schema version 1

* Remove concrete profiles `in_vitro_system` and `in_vivo_system`.
* Add optional `diseases` (linkTo ControlledTerm) to capture diseases relevant to the measurement context.
* Add optional `date_obtained`.
* Add optional `collection_geographical_location`.
* Remove `author_metadata` from abstract biosample profile; concrete biosample types use `mixins.json#/author_metadata`.
* Add dependentSchemas for lower_bound_age, upper_bound_age, and age_units (mutual requirement when any is present; merged into concrete profiles that use `$merge` of biosample dependentSchemas).
* Add optional `treatments` array (linkTo Treatment) for ChEBI/UniProt treatment agents.
* Remove treatment.
* Initial abstract schema definition.
