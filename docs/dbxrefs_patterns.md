# `dbxrefs` Regular Expressions

Reference for the `dbxrefs` external identifiers accepted by IGVF schemas. Every
`dbxrefs` value is an array of unique strings. Each owning schema supplies an
anchored regular expression for its archive level.

## Shared mixin

`mixins.json#/dbxrefs` supplies JSON-LD annotations and common array constraints:
`@type: @id`, `rdfs:subPropertyOf: rdfs:seeAlso`, `type: array`, and
`uniqueItems: true`. It intentionally has no item pattern. Biosample, Library,
SequenceFileSet, and MatrixFileSet define their own patterns.

ControlledTerm defines `dbxrefs` locally and is unchanged by this model.

## Biosample

Concrete Tissue, PrimaryCellCulture, Organoid, and CellLine objects inherit:

```regex
^(EGA:EGAN\d+|SRA:SRS\d+|ENA:ERS\d+)$
```

Accepted sample-level identifiers:

- `EGA:EGAN12345`
- `SRA:SRS12345`
- `ENA:ERS12345`

BioSample accessions such as NCBI `SAMN` and EBI `SAMEA` are deliberately
excluded from Biosample. IGVF models these external biomaterial records on
Library using the `Biomaterial:` prefix.

## Library

Concrete DropletBasedLibrary and PlateBasedLibrary objects inherit:

```regex
^(Biomaterial:SAMN\d+|Biomaterial:SAMEA\d+|SRA:SRS\d+|ENA:ERS\d+|GEO:GSM\d+|SRA:SRX\d+|ENA:ERX\d+)$
```

Accepted identifiers:

- NCBI biomaterial and sample records: `Biomaterial:SAMN53299868`, `SRA:SRS12345`
- EBI biomaterial and ENA sample counterparts: `Biomaterial:SAMEA1234567`, `ENA:ERS12345`
- GEO samples: `GEO:GSM12345`
- SRA/ENA experiments: `SRA:SRX12345`, `ENA:ERX12345`

`Biomaterial:` is an IGVF modeling prefix that makes the Library placement of
the archive-issued SAMN/SAMEA accession explicit; it is not an archive-issued
accession prefix.

SRX and ERX remain on Library because SRA and ENA experiments describe library
and sequencing metadata. An experiment can own multiple runs, so SRX/ERX must
not be treated as one-to-one aliases for SRR/ERR.

The previous `EGA:EGAX` and `GEO-obsolete:GSM` forms are no longer accepted.
During schema upgrade, rejected legacy values are removed from `dbxrefs` and
copied verbatim into admin-only `notes`.

## SequenceFileSet

```regex
^(SRA:SRR\d+|ENA:ERR\d+)$
```

SequenceFileSet represents the files from a sequencing run, so it accepts NCBI
SRA run identifiers such as `SRA:SRR123456` and corresponding ENA run
identifiers such as `ENA:ERR123456`.

## MatrixFileSet

```regex
^(GEO:GSE\d+|ENA:ERP\d+)$
```

MatrixFileSet accepts GEO series identifiers such as `GEO:GSE12345` and
same-level ENA study identifiers such as `ENA:ERP123456`. GSE and ERP are not
guaranteed to be one-to-one; an ERP should be supplied only when the matrix
dataset has a corresponding ENA study.

## ControlledTerm

ControlledTerm remains unchanged:

```regex
^(PMID:[0-9]+|DOI:10\.[0-9]+/.+|CAS:\d{2,7}-\d{2}-\d)$
```

It accepts literature and chemical-registry identifiers such as
`PMID:12345678`, `DOI:10.1038/s41586-020-2649-2`, and `CAS:50-00-0`.

## Notes

- Prefixes are case-sensitive and mandatory.
- Patterns are anchored and do not tolerate leading or trailing whitespace.
- Archive accession digit counts remain `\d+`, matching the existing repository
  convention. Enforcing documented accession widths is outside this change.
- `dbxrefs` arrays require at least one identifier; submitters must omit the
  property instead of submitting an empty array.
- Upgrade logic does not move identifiers between related IGVF objects because
  the correct target cannot be inferred reliably. It preserves rejected values
  in admin-only `notes` for manual reconciliation.
