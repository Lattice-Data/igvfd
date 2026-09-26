# Image Changelog

### Schema version 2

* Update `aliases` regex to anchor at true end of input with `(?![\s\S])` rather than `$`.
* Update `aliases` regex to allow only single spaces between words.
* Preserve `aliases` rejected by the updated regex in `notes` during upgrade.

### Minor changes since schema version 1

* Update `aliases` regex to accept `shyam-prabhakar` prefix.
* Update `aliases` regex to accept `john-tsang` prefix.
* Update `aliases` regex to accept `silvia-domcke` prefix.
* Update `aliases` regex to accept `will-allen` prefix.
