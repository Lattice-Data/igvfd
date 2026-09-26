## Changelog for experimental_condition.json

### Minor changes since schema version 1

* Update `aliases` regex to anchor at true end of input with `(?![\s\S])` rather than `$`.
* Update `aliases` regex to allow only single spaces between words.
* Update `aliases` regex to accept `shyam-prabhakar` prefix.
* Update `aliases` regex to accept `john-tsang` prefix.
* Update `aliases` regex to accept `silvia-domcke` prefix.
* Update `aliases` regex to accept `will-allen` prefix.
* Add controlled_term.
* Add lower_bound_duration.
* Add upper_bound_duration.
* Add duration_units.
* Require lower_bound_duration, upper_bound_duration, and duration_units together when any is present.

### Schema version 1

* Initial release defining experimental condition schema with quantitative and qualitative condition types.
