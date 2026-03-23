# Biosample Changelog

- Add dependentSchemas for lower_bound_age, upper_bound_age, and age_units (mutual requirement when any is present; merged into concrete profiles that use `$merge` of biosample dependentSchemas).
- Add optional `treatments` array (linkTo Treatment) for ChEBI/UniProt treatment agents.
- Remove treatment.
- Initial abstract schema definition.
