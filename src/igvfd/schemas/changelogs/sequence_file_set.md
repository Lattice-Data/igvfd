# Sequence File Set Changelog

## Schema version 2

* Add is_pilot_order.
* Require is_pilot_order and CRO_order together (both present or both absent).

## Schema version 1

* Initial release, replacing SequencingRun.
* Add required library link.
* Add CRO_order (moved from Library).
* Add Ultima Genomics support with untrimmed_cram and trimmed_cram.
* Enforce mutual exclusivity between Illumina (FASTQ) and Ultima (CRAM) file slots.
