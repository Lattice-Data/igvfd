# Biosample Changelog

- Remove concrete profiles `in_vitro_system` and `in_vivo_system`.
- Add optional `diseases` (linkTo ControlledTerm) to capture diseases relevant to the measurement context.
- Add optional `date_obtained`.
- Add optional `collection_geographical_location`.
- Remove `author_metadata` from abstract biosample profile; concrete biosample types use `mixins.json#/author_metadata`.
- Add dependentSchemas for lower_bound_age, upper_bound_age, and age_units (mutual requirement when any is present; merged into concrete profiles that use `$merge` of biosample dependentSchemas).
- Add optional `treatments` array (linkTo Treatment) for ChEBI/UniProt treatment agents.
- Remove treatment.
- Initial abstract schema definition.
