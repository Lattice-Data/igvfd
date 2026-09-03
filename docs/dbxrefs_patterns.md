# `dbxrefs` Regular Expressions

Reference for the `dbxrefs` external identifiers accepted by IGVF schemas. Every
`dbxrefs` value is an array of unique strings. Each owning schema supplies an
anchored regular expression for its archive level.

## Shared mixin

`mixins.json#/dbxrefs` supplies JSON-LD annotations and common array constraints:
`@type: @id`, `rdfs:subPropertyOf: rdfs:seeAlso`, `type: array`, and
`uniqueItems: true`. It intentionally has no item pattern. Library,
SequenceFileSet, and MatrixFileSet mix it in and define their own patterns.

snovault merges `mixinProperties` per key rather than replacing the whole property,
so redefining `dbxrefs` locally to add `items`/`minItems`/`submissionExample` still
inherits `@type`, `rdfs:subPropertyOf`, `title`, and `description` from the mixin.
Verified against `load_schema` for all three owners; the local `type` and
`uniqueItems` restatements are therefore redundant but harmless.

ControlledTerm defines `dbxrefs` locally and is unchanged by this model.

## Biosample

Biosample has no `dbxrefs` property, and does not mix in `mixins.json#/dbxrefs`.
Tissue, PrimaryCellCulture, Organoid, and CellLine accept no external
identifiers; because `additionalProperties` is `false`, submitting `dbxrefs` to
any of them is rejected regardless of the value.

Archive sample records are modeled on Library instead — under the `Biomaterial:`
prefix for the sample registries, and under the archives' own `SRA:SRS` and
`ENA:ERS` prefixes for SRA and ENA samples.

The goal is that an accession's position in the archive hierarchy determines which
object owns it, matching how the run and study levels sit on SequenceFileSet and
MatrixFileSet. It is worth being precise about what this does *not* fix: the two
patterns being replaced were already disjoint, so no accession string was ever
accepted by both Biosample and Library, and there was no pre-existing dual-home
ambiguity to remove. This is a modeling change, not a bug fix, and it is paid for
with a breaking version bump on six types. No production object carries `dbxrefs`
today, so no re-filing is actually pending; see [Migration](#migration) for how a
stray value would be handled and [Known gaps](#known-gaps) for levels that remain
unrepresentable.

## Library

Concrete DropletBasedLibrary and PlateBasedLibrary objects inherit:

```regex
^(Biomaterial:SAM(E|N|D)(A|G)?\d+|Biomaterial:EGAN\d+|SRA:SRS\d+|ENA:ERS\d+|GEO:GSM\d+|SRA:SRX\d+|ENA:ERX\d+|EGA:EGAX\d+)(?![\s\S])
```

Accepted sample-level identifiers:

- EBI BioSamples records: `Biomaterial:SAME1234567`
- NCBI BioSample records: `Biomaterial:SAMN53299868`
- DDBJ BioSample records: `Biomaterial:SAMD1234567`
- Assay samples: `Biomaterial:SAMEA1234567`, `Biomaterial:SAMNA12345`, `Biomaterial:SAMDA12345`
- Sample groups: `Biomaterial:SAMEG1234567`, `Biomaterial:SAMNG12345`, `Biomaterial:SAMDG12345`
- EGA samples: `Biomaterial:EGAN12345`
- SRA and ENA samples: `SRA:SRS12345`, `ENA:ERS12345`

Accepted experiment-level identifiers:

- GEO samples: `GEO:GSM12345`
- SRA and ENA experiments: `SRA:SRX12345`, `ENA:ERX12345`
- EGA experiments: `EGA:EGAX12345`

`Biomaterial:` is an IGVF modeling prefix that marks an archive sample-registry
record placed on Library; it is not an archive-issued prefix. The BioSample part
follows the [BioSamples accession format](https://www.ebi.ac.uk/biosamples/docs/faq):
`SAM`, then `E`, `N`, or `D` for the archive the sample was first submitted to
(EMBL-EBI, NCBI, DDBJ), then optionally `A` for an assay sample or `G` for a sample
group, then digits. `Biomaterial:` also covers EGA's `EGAN`.

The optional `A`/`G` qualifier is accepted after any of the three archive letters.
That matches the FAQ's wording and is narrower than
[Bioregistry](https://bioregistry.io/registry/biosample), which registers
`^SAM[NED](\w)?\d+$` — any word character after any archive letter. In practice the
qualifier is seen mainly on the EBI letter (`SAMEA`, `SAMEG`), so `SAMNA`-style forms
are accepted rather than expected; the pattern errs toward accepting a real accession
over rejecting one.

`SAMED` is *not* accepted, because the letter after `E`/`N`/`D` can only be `A` or
`G`; `SAMED` is malformed rather than a DDBJ-via-EBI form. Every BioSample form the
old Biosample pattern accepted is accepted here, so any legacy `BioSample:SAM*`
value has a `Biomaterial:` counterpart.

GEO samples sit at the experiment level because a GEO sample record describes a
library and its sequencing, not a biosample. SRX and ERX are on Library for the
same reason: an SRA or ENA experiment describes library and sequencing metadata,
and it can own multiple runs, so SRX/ERX must not be treated as one-to-one
aliases for SRR/ERR.

`GEO-obsolete:GSM` is no longer accepted.

## SequenceFileSet

```regex
^(SRA:SRR\d+|ENA:ERR\d+)(?![\s\S])
```

SequenceFileSet represents the files from a sequencing run, so it accepts NCBI
SRA run identifiers such as `SRA:SRR123456` and corresponding ENA run
identifiers such as `ENA:ERR123456`.

## MatrixFileSet

```regex
^(GEO:GSE\d+|SRA:SRP\d+|ENA:ERP\d+)(?![\s\S])
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

No production object currently carries `dbxrefs`, so these upgrades have nothing to
migrate in practice. The preservation described here is a precaution rather than a
migration plan: if a value does turn up, it is recorded instead of silently dropped.

Rejected values are removed from `dbxrefs` and appended verbatim to `notes`, which is
`admin_only`, and `dbxrefs` is dropped entirely when nothing valid remains. Upgrades
do not move identifiers between objects, because the correct target object cannot be
inferred. Every Biosample `dbxrefs` value is preserved this way, since the property is
gone. Should a value ever need re-filing by hand:

| Legacy value | Held by | Re-file as | On |
| --- | --- | --- | --- |
| `EGA:EGAN12345` | Biosample | `Biomaterial:EGAN12345` | Library |
| `BioSample:SAMN…`, `BioSample:SAMD…`, `BioSample:SAMEA…`, `BioSample:SAMEG…` | Biosample | `Biomaterial:SAMN…` etc. | Library |
| `SRA:SRS12345`, `ENA:ERS12345` | Biosample | unchanged | Library |

The Library pattern accepts every BioSample form the old Biosample pattern did, so
each legacy `BioSample:SAM*` value re-files as `Biomaterial:SAM*` with the digits
and letters unchanged. Legacy `EGA:EGAX` and `GEO:GSM` values already on Library
remain valid and are not touched.

## Known gaps

Sample and experiment levels are well covered; higher and archive-specific levels
are not. These are currently not representable on any object:

| Archive | Missing level(s) |
| --- | --- |
| EGA | run (`EGAR`), study (`EGAS`), dataset (`EGAD`) |
| DDBJ | DRA sample (`DRS`), experiment (`DRX`), run (`DRR`), study (`DRP`) |
| NCBI / EBI | BioProject (`PRJNA`, `PRJEB`) |

A sample-level accession on a multiplexed Library is unconstrained. `samples` is
`minItems: 1` with no upper bound, and multi-sample libraries are real, so a library
prepared from several biosamples can carry several `Biomaterial:SAM*` values in one
flat array with nothing recording which accession belongs to which entry in `samples`.
JSON Schema cannot express "a sample-level dbxref implies exactly one sample", and no
audit enforces it, so on a multiplexed library these values should be read as
identifying the set of samples rather than any one of them. Relatedly, a Tissue or
Organoid that is not yet part of a library has nowhere to record its BioSample
accession, since Biosample no longer has `dbxrefs`.

Study-level accessions (`GEO:GSE`, `SRA:SRP`, `ENA:ERP`) are also accepted only on
MatrixFileSet. A submission with sequence data but no matrix files has nowhere to
record the study that groups the `SRR`/`ERR` values on its SequenceFileSets.

Declaring `dbxrefs` on `file_set.json` does not close this cleanly, despite being
the obvious move. `file_set.json` has exactly two concrete subtypes, but a locally
declared property wins over the inherited one, so SequenceFileSet's run-only pattern
would still shadow a study pattern on the parent; and dropping the local declaration
would trade the run level away for the study level. The remaining options all cost
something: put the union of run and study on the parent and accept that a study
accession is then valid on two object types, add the study level to SequenceFileSet's
own pattern with the same consequence, or leave the hole. That is a modeling decision
rather than a mechanical fix, which is why it is recorded here instead of applied.

DDBJ BioSample records are accepted as `Biomaterial:SAMD`, so DDBJ is representable
at the BioSample-registry level only; its DRA accessions are not. BioProject
accessions are alternate identifiers for the same study as `SRP`/`ERP`, so that
level is covered, but a submitter holding only a `PRJNA` has nothing to submit. An
EGA-only or DDBJ-only submission can record part of the hierarchy and not the rest.
Whether to add any of these depends on which archives Lattice actually deposits to
at each level.

Prefixes are also not registered in `namespaces.json`, which maps a CURIE prefix to
a resolvable URL. `GEO` is registered; `Biomaterial`, `SRA`, `ENA`, and `EGA` are
not, so a consumer cannot expand these identifiers to URLs. `SRA`/`ENA`/`EGA` were
already unregistered before this change; `Biomaterial` adds one more. Note that
`Biomaterial:` intentionally covers several registries at once (five BioSample
prefixes plus EGA's `EGAN`), so resolving it requires switching on the accession
body rather than the prefix.

## Notes

- Prefixes are case-sensitive and mandatory.
- Patterns are anchored at both ends, so leading and trailing whitespace and any
  surrounding text are rejected. The closing assertion is `(?![\s\S])`, a negative
  lookahead for any character, rather than `$`. This matters: `jsonschema` compiles
  `pattern` with Python `re`, where `$` also matches immediately before a trailing
  newline, while ECMA-262 — the dialect JSON Schema specifies — matches `$` only at
  end of input without the `m` flag. With `$` the same published profile therefore
  validated differently depending on the consumer, and because `uniqueItems` treats
  `GEO:GSM1` and the same value plus a newline as distinct strings, one object could
  carry the same accession twice. `(?![\s\S])` behaves identically in Python `re` and
  ECMA-262 — verified on both engines — so the profile now means one thing. Note
  ECMA-262 has no `\Z` anchor; in JavaScript it matches a literal `Z`, so it is not
  the construct to reach for.
- The upgrade helper filters with `search`, matching how `jsonschema` applies
  `pattern`, so it accepts exactly what the validator accepts. With the patterns
  anchored at true end of input, `search` and `fullmatch` coincide.
- ControlledTerm's `dbxrefs` still ends with `$` and is out of scope here. Narrowing
  it would need its own version bump and upgrade step, since unlike the two new
  file-set properties it may already hold data.
- Archive accession digit counts remain `\d+`, matching the existing repository
  convention. Enforcing documented accession widths is outside this change.
- The Library, SequenceFileSet, and MatrixFileSet `dbxrefs` arrays require at
  least one identifier; submitters must omit the property instead of submitting
  an empty array. ControlledTerm's `dbxrefs` is unchanged and still permits an
  empty array.
- `src/igvfd/upgrade/library.py` keeps a compiled copy of the Library pattern for
  the upgrade filter, guarded from both directions.
  `test_library_upgrade_dbxref_pattern_matches_schema` asserts it equals the current
  schema pattern, so widening one without the other fails CI.
  `test_library_upgrade_dbxref_pattern_is_frozen` pins it to a literal, so the
  released 4→5 and 5→6 steps cannot be made to strip something different after the
  fact. When the schema pattern next changes, freeze the constant under a versioned
  name for the existing steps and add a new constant plus step for the new pattern.
- Should a preserved value ever appear, it can be found by the marker string `Legacy
  dbxrefs removed during schema upgrade`, which is stable and should not be reworded.
  `notes` is indexed as `type: text` at `embedded.notes`, so it is queryable in
  OpenSearch, though it is not exposed in `src/igvfd/searches/configs/` and so is not
  available as a search facet or column.
