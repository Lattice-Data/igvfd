# Sequence File Set Changelog

## Minor changes since schema version 2

* Add optional dbxrefs for SRA and ENA run identifiers.
* Extend sequencing_platform enum list to include Illumina NovaSeq 6000.
* Extend sequencing_platform enum list to include Illumina NovaSeq X.
* Extend sequencing_platform enum list to include Illumina NovaSeq X Plus.
* Extend sequencing_platform enum list to include Ultima Genomics UG 200.

## Schema version 2

* Add is_pilot_order.
* Require is_pilot_order and CRO_order together (both present or both absent).

## Schema version 1

* Initial release, replacing SequencingRun.
* Add required library link.
* Add CRO_order (moved from Library).
* Add Ultima Genomics support with untrimmed_cram and trimmed_cram.
* Enforce mutual exclusivity between Illumina (FASTQ) and Ultima (CRAM) file slots.
