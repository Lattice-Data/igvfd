# In Vivo System Changelog

* Add deprecation notice to use cell_line for new submissions.
* Add `author_metadata` via `mixins.json#/author_metadata` (shared with abstract biosample profile).
* Add host_tissue.
* Add intended_cell_types.

## Schema version 1

* Initial release
* Concrete schema inheriting from abstract Biosample class
* Added in vivo system-specific properties: classification (xenograft), host (optional linkTo Donor)
