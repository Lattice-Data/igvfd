## Changelog for experimental_condition.json

### Schema version 3

* Remove `condition`, `value`, `units` and `text_value`.
* Replace `controlled_term` with `controlled_terms`, a list of ChEBI, UniProt, EFO or other ontology terms for the agents or factors in the condition.
* Replace `lower_bound_duration`, `upper_bound_duration` and `duration_units` with `lower_bound_time_point`, `upper_bound_time_point` and `time_point_units`, the time from the start of the condition to sample collection.
* Require `controlled_terms` or `description`.
* Require `upper_bound_time_point` to be greater than or equal to `lower_bound_time_point`.
* Change `summary` to the `description` when present, otherwise the controlled term names and the time point, for example "anti-CD3E_HUMAN and IL2_HUMAN, 8 hours" or "INS_HUMAN, 2-3 hours".
* During upgrade, `controlled_term` moves into `controlled_terms`, the duration range becomes the time point range, and `text_value` becomes `description` when there is none. Removed values are preserved in `notes`. A condition left with neither controlled terms nor a description gets a description built from its `condition`, `value` and `units`.

### Minor changes since schema version 2

* Add `chemical treatment` and `protein treatment` to `condition`.
* Require `controlled_term` or `text_value` for `chemical treatment` and `protein treatment`.
* Add `mg/kg`, `mg/mL`, `mM`, `ng/mL`, `nM`, `μg/kg`, `μg/mL`, and `μM` to `units`.
* Restrict `units` for `chemical treatment` and `protein treatment` to `mg/kg`, `mg/mL`, `mM`, `ng/mL`, `nM`, `percent`, `μg/kg`, `μg/mL`, `μM`, and `kPa`; other conditions do not accept the treatment amount units.
* Require `upper_bound_duration` to be greater than or equal to `lower_bound_duration`.
* Change `summary` to a human readable sentence describing the condition, for example "Chemical treatment with ethanol at 3% for 4 hours".

### Schema version 2

* Update `aliases` regex to anchor at true end of input with `(?![\s\S])` rather than `$`.
* Update `aliases` regex to allow only single spaces between words.
* Update `aliases` regex to accept `shyam-prabhakar` prefix.
* Update `aliases` regex to accept `john-tsang` prefix.
* Update `aliases` regex to accept `silvia-domcke` prefix.
* Update `aliases` regex to accept `will-allen` prefix.
* Preserve `aliases` rejected by the updated regex in `notes` during upgrade.

### Minor changes since schema version 1

* Add controlled_term.
* Add lower_bound_duration.
* Add upper_bound_duration.
* Add duration_units.
* Require lower_bound_duration, upper_bound_duration, and duration_units together when any is present.

### Schema version 1

* Initial release defining experimental condition schema with quantitative and qualitative condition types.
