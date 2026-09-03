# `dbxrefs` Regular Expressions

Reference for the `dbxrefs` external identifiers accepted by IGVF schemas. Every
`dbxrefs` value is an array of unique strings. Each owning schema supplies an
anchored regular expression for its archive level.

## Shared mixin

`mixins.json#/dbxrefs` supplies JSON-LD annotations and common array constraints:
`@type: @id`, `rdfs:subPropertyOf: rdfs:seeAlso`, `type: array`, and
`uniqueItems: true`. It intentionally has no item pattern. Library,
SequenceFileSet, and MatrixFileSet mix it in and define their own patterns.

ControlledTerm defines `dbxrefs` locally and is unchanged by this model.

## Biosample

Biosample has no `dbxrefs` property, and does not mix in `mixins.json#/dbxrefs`.
Tissue, PrimaryCellCulture, Organoid, and CellLine accept no external
identifiers; because `additionalProperties` is `false`, submitting `dbxrefs` to
any of them is rejected regardless of the value.

Archive sample records are modeled on Library instead — under the `Biomaterial:`
prefix for the sample registries, and under the archives' own `SRA:SRS` and
`ENA:ERS` prefixes for SRA and ENA samples. Every accession therefore has exactly
one valid home.

## Library

Concrete DropletBasedLibrary and PlateBasedLibrary objects inherit:

```regex
^(Biomaterial:SAM(N|D|E[ADG])\d+|Biomaterial:EGAN\d+|SRA:SRS\d+|ENA:ERS\d+|GEO:GSM\d+|SRA:SRX\d+|ENA:ERX\d+|EGA:EGAX\d+)$
```

Accepted sample-level identifiers:

- NCBI BioSample records: `Biomaterial:SAMN53299868`
- DDBJ BioSample records: `Biomaterial:SAMD1234567`
- EBI BioSamples records: `Biomaterial:SAMEA1234567`, `Biomaterial:SAMED1234567`
- EBI BioSamples groups: `Biomaterial:SAMEG1234567`
- EGA samples: `Biomaterial:EGAN12345`
- SRA and ENA samples: `SRA:SRS12345`, `ENA:ERS12345`

Accepted experiment-level identifiers:

- GEO samples: `GEO:GSM12345`
- SRA and ENA experiments: `SRA:SRX12345`, `ENA:ERX12345`
- EGA experiments: `EGA:EGAX12345`

`Biomaterial:` is an IGVF modeling prefix that marks an archive sample-registry
record placed on Library; it is not an archive-issued prefix. It covers the five
BioSample prefixes the archives issue — `SAMN` (NCBI), `SAMD` (DDBJ), and
`SAMEA`/`SAMED`/`SAMEG` (EBI) — plus EGA's `EGAN`. Forms that no archive issues,
such as `SAME`, `SAMNA`, and `SAMDG`, are rejected.

GEO samples sit at the experiment level because a GEO sample record describes a
library and its sequencing, not a biosample. SRX and ERX are on Library for the
same reason: an SRA or ENA experiment describes library and sequencing metadata,
and it can own multiple runs, so SRX/ERX must not be treated as one-to-one
aliases for SRR/ERR.

`GEO-obsolete:GSM` is no longer accepted.

## SequenceFileSet

```regex
^(SRA:SRR\d+|ENA:ERR\d+)$
```

SequenceFileSet represents the files from a sequencing run, so it accepts NCBI
SRA run identifiers such as `SRA:SRR123456` and corresponding ENA run
identifiers such as `ENA:ERR123456`.

## MatrixFileSet

```regex
^(GEO:GSE\d+|SRA:SRP\d+|ENA:ERP\d+)$
```

MatrixFileSet accepts GEO series identifiers such as `GEO:GSE12345` plus the
study-level accessions on both archive sides: `SRA:SRP123456` and
`ENA:ERP123456`. These are not guaranteed to be one-to-one; a study accession
should be supplied only when the matrix dataset has a corresponding archive
study.

## ControlledTerm

ControlledTerm remains unchanged:

```regex
^(PMID:[0-9]+|DOI:10\.[0-9]+/.+|CAS:\d{2,7}-\d{2}-\d)$
```

It accepts literature and chemical-registry identifiers such as
`PMID:12345678`, `DOI:10.1038/s41586-020-2649-2`, and `CAS:50-00-0`.

## Migration

Upgrades do not move identifiers between related IGVF objects, because the
correct target object cannot be inferred reliably. Rejected values are removed
from `dbxrefs` and appended verbatim to `notes`, which is `admin_only`, and
`dbxrefs` is dropped entirely when nothing valid remains. Re-filing is manual.

Every Biosample `dbxrefs` value is preserved this way, since the property is
gone. The table below gives the re-filing target for each legacy form:

| Legacy value | Held by | Re-file as | On |
| --- | --- | --- | --- |
| `EGA:EGAN12345` | Biosample | `Biomaterial:EGAN12345` | Library |
| `BioSample:SAMN…`, `BioSample:SAMD…`, `BioSample:SAMEA…`, `BioSample:SAMEG…` | Biosample | `Biomaterial:SAMN…` etc. | Library |
| `SRA:SRS12345`, `ENA:ERS12345` | Biosample | unchanged | Library |
| `BioSample:SAME…`, `BioSample:SAMNA…`, `BioSample:SAMNG…`, `BioSample:SAMDA…`, `BioSample:SAMDG…` | Biosample | no target | — |
| `GEO-obsolete:GSM12345` | Library | `GEO:GSM12345` | Library |

The five forms with no target are prefixes no archive issues. The old Biosample
pattern was `BioSample:SAM(E|N|D)(A|G)?\d+`, whose optional `(A|G)` group admitted
them by accident alongside the four real prefixes. Values in those forms do not
correspond to real accessions, so they remain in `notes` with nothing to re-file
them as. Legacy `EGA:EGAX` and `GEO:GSM` values already on Library are unaffected
by this change and are not migrated.

## Notes

- Prefixes are case-sensitive and mandatory.
- Patterns are anchored, so leading whitespace and surrounding text are rejected.
  JSON Schema `pattern` is a search and `$` also matches immediately before a
  trailing newline, so a value with a single trailing newline validates. The
  upgrade helper uses `search` for exactly this reason, so it accepts precisely
  what the schema accepts and never migrates a valid value into `notes`. Closing
  the newline gap itself would mean `\Z` across every pattern in the repository,
  which is outside this change.
- Archive accession digit counts remain `\d+`, matching the existing repository
  convention. Enforcing documented accession widths is outside this change.
- The Library, SequenceFileSet, and MatrixFileSet `dbxrefs` arrays require at
  least one identifier; submitters must omit the property instead of submitting
  an empty array. ControlledTerm's `dbxrefs` is unchanged and still permits an
  empty array.
- `src/igvfd/upgrade/library.py` keeps a compiled copy of the Library pattern for
  the upgrade filter. `test_library_upgrade_dbxref_pattern_matches_schema` asserts
  it equals the schema pattern, so widening one without the other fails CI.
