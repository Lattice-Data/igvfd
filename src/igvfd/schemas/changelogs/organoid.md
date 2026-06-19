# Changelog for organoid.json

## Schema version 3

* Rename hash_index to multiplexing_barcodes.

## Minor changes since schema version 2

* Add developmental_stages.
* Add `origin_cell_types`.

## Schema version 2

* Bump schema_version default to 2.
* Inherit selection_kits from abstract biosample profile.
* Inherit selection_methods from abstract biosample profile.
* Inherit selection_markers from abstract biosample profile.
* Remove inherited enrichment_method.
* Remove inherited enrichment_markers.

* Use inherited `date_obtained` from abstract biosample profile.
* Use inherited `collection_geographical_location` from abstract biosample profile.

## Schema version 1

* Initial release
