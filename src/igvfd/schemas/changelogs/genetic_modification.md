# Genetic Modification Changelog

### Schema version 3

* Update `aliases` regex to anchor at true end of input with `(?![\s\S])` rather than `$`.
* Update `aliases` regex to allow only single spaces between words.
* Update `aliases` regex to accept `shyam-prabhakar` prefix.
* Update `aliases` regex to accept `john-tsang` prefix.
* Update `aliases` regex to accept `silvia-domcke` prefix.
* Update `aliases` regex to accept `will-allen` prefix.
* Preserve `aliases` rejected by the updated regex in `notes` during upgrade.

### Minor changes since schema version 2

* Add *guide_rna_files*.
* Add *targeted_genes*.
* Require *strategy* to be *knockout mutation* when *targeted_genes* is submitted.

## Schema version 2

- Rename modality to strategy.
- Adjust strategy enum list to replace activation with activation screen.
- Adjust strategy enum list to replace base editing with base editing screen.
- Adjust strategy enum list to replace cutting with cutting screen.
- Adjust strategy enum list to replace interference with interference screen.
- Adjust strategy enum list to replace knockout with knockout screen.
- Adjust strategy enum list to replace localizing with localizing screen.
- Adjust strategy enum list to replace prime editing with prime editing screen.
- Extend strategy enum list to include knockout mutation.

## Schema version 1

- Initial schema definition for genetic modifications applied to biological samples.
