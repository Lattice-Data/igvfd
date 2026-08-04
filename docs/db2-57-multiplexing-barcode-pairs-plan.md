# Implementation Plan: DB2-57 — allow paired probe barcodes in `multiplexing_barcodes`

Branch: `db2-57` (off `dev`).

## Goal

`biosample.multiplexing_barcodes` currently accepts a 10x Flex probe barcode (`BC001`–`BC016`) or a
CRISPR Flex barcode (`CR001`–`CR016`) as separate entries. Submitters need to record the pairing of
the two on a single entry, e.g. `BC001+CR001`, for any combination of the existing `BC` and `CR`
numbers.

The change is **purely relaxing**: every string valid today stays valid, and the only newly accepted
form is `BC0xx+CR0yy`. Therefore **no `schema_version` bump and no upgrade step** — existing objects
cannot become invalid.

## Verified facts (current code)

| Fact | Evidence |
|---|---|
| The regex exists in exactly one place | `src/igvfd/schemas/biosample.json:643` — no other schema, type, or audit hard-codes barcode syntax (repo-wide grep for `BC0(0[1-9]`) |
| Concrete biosample types inherit it via mixin, not copy | `tissue.json`, `cell_line.json`, `organoid.json`, `primary_cell_culture.json` all `$ref` `biosample.json#/properties` |
| Audits check presence only, never format | `src/igvfd/audit/library.py:73-178` (`_samples_missing_multiplexing_barcodes` / `_samples_with_multiplexing_barcodes`) |
| Mappings store the field as a plain keyword; the pattern is not part of the mapping | `src/igvfd/mappings/{tissue,cell_line,organoid,primary_cell_culture,*_library}.json` → **no mapping regeneration needed** |
| Search configs reference the field only as a fuzzy searchable field | `src/igvfd/searches/configs/*.py`, `biosample.json:667` → **no search config change** |
| Inserts are schema-validated when loaded | `workbook` fixture + `test_load_workbook` in `src/igvfd/tests/test_views.py:102` |
| The compiled schema is validated as Draft 2020-12 | `test_profiles` in `src/igvfd/tests/test_views.py:278` |
| Existing regex tests to extend | `src/igvfd/tests/test_types_biosample_common.py:131-185` (valid/invalid parametrized over all 4 concrete types) |

## Regex change

`src/igvfd/schemas/biosample.json`, `multiplexing_barcodes.items.pattern`.

Only the first alternative changes — an optional `+CR0yy` suffix is appended to the `BC0xx` branch:

```
BC0(0[1-9]|1[0-6])          →  BC0(0[1-9]|1[0-6])(\+CR0(0[1-9]|1[0-6]))?
```

Full new pattern (as it appears in the JSON file, with `\\+` for the literal `+`):

```
^(BC0(0[1-9]|1[0-6])(\\+CR0(0[1-9]|1[0-6]))?|CR0(0[1-9]|1[0-6])|[A-D]-[A-H](0[1-9]|1[0-2])|SCALE-[A-H]([1-9]|1[0-2])|P(0[1-9]|[1-9][0-9])-[A-H]([1-9]|1[0-2])|([1-9]|1[0-2])[A-H](-([1-9]|1[0-2])[A-H])?|[A-D][0-9]{4})$
```

Behaviour verified against the existing test corpus before writing this plan:

| Input class | Old | New |
|---|---|---|
| `P01-A1`, `SCALE-A1`, `BC001`, `BC016`, `CR001`, `CR016`, `A-A01`, `D-H12`, `9A-9C`, `10H`, `A0251`, `P02-D1` | accept | accept (unchanged) |
| every string in the current `..._invalid` test list, plus `BC017`, `BC000`, `CR017` | reject | reject (unchanged) |
| `BC001+CR001`, `BC016+CR016`, `BC009+CR012` | reject | **accept** |
| `CR001+BC001`, `BC001+BC002`, `BC001+CR017`, `BC017+CR001`, `BC001+`, `+CR001`, `BC001+CR001+CR002`, `BC001 + CR001`, `bc001+cr001` | reject | reject |

### Deliberate scope limits

1. **Order is fixed as `BC` then `CR`.** The probe barcode identifies the sample, the CRISPR barcode
   qualifies it; a single canonical order keeps values comparable in facets and search. `CR001+BC001`
   stays invalid.
2. **Exactly two components.** No `BC001+CR001+CR002` chains.
3. **Only the `BC`/`CR` families pair.** `+` is not introduced for plate-well or hashtag-oligo forms.
4. **No same-family pairs** (`BC001+BC002`, `CR001+CR002`).

If any of these turn out to be wrong for the submitters, each is a one-alternative edit to the same
branch of the regex, still without a version bump.

### Description update

The `multiplexing_barcodes` description already enumerates the supported strategies. Extend the
probe-barcoding clause so the pair form is documented where submitters read it, e.g. after
`CRISPR Flex CR001–CR016`: "…, a paired probe and CRISPR Flex barcode written as `BC001+CR001`, …".
Leave `submissionExample` as `["P01-A1"]` (it illustrates the common plate-well case).

## Changelogs (no version bump)

Per `docs/updating_schemas.md` ("Add entries to all affected schemas when there is a change to
properties which are inherited or merged into other schemas"), all five changelogs get the entry,
added at the top of the existing `## Minor changes since schema version 3` section:

* `src/igvfd/schemas/changelogs/biosample.md`
* `src/igvfd/schemas/changelogs/cell_line.md`
* `src/igvfd/schemas/changelogs/organoid.md`
* `src/igvfd/schemas/changelogs/primary_cell_culture.md`
* `src/igvfd/schemas/changelogs/tissue.md`

Wording follows the stylebook row for a regex change ("Update \[property name\] regex to
\[description of regex\]."):

```
* Update multiplexing_barcodes regex to allow a paired 10x Flex probe and CRISPR Flex barcode, such as BC001+CR001.
```

## Inserts

Add pair values to inserts so the new form is exercised by the workbook load (which schema-validates
every insert) and is visible in the local dev data.

1. `src/igvfd/tests/data/inserts/cell_line.json` — `lattice:cell-line-reference`
   (uuid `9b6df595-…`): add `"multiplexing_barcodes": ["BC001+CR001"]`.
2. `src/igvfd/tests/data/inserts/organoid.json` — `lattice:organoid-brain`
   (uuid `71f2bbec-…`): add `"multiplexing_barcodes": ["BC016+CR016"]` (covers the upper bound of
   both ranges).

**Why these two records:** neither is referenced by any library insert, so the library-side audits
`audit_library_samples_missing_multiplexing_barcodes` /
`audit_library_samples_unexpected_multiplexing_barcodes` (`src/igvfd/audit/library.py`) cannot fire
on them and no existing audit expectation changes. Do **not** add pair barcodes to the tissue
inserts: `414e5c99-…` and `2cc69a5c-…` are linked from `lattice:droplet-library-multiplexed`, whose
`multiplexing_method` is `antibody hashing`, so a probe-barcode value there would be semantically
wrong.

Insert counts stay the same, so `test_load_workbook` needs no update.

## Tests

`src/igvfd/tests/test_types_biosample_common.py` — extend the two existing parametrized lists (each
case runs against all four concrete types, so keep the additions tight).

Add to `test_biosample_multiplexing_barcodes_valid`:

* `['BC001+CR001']` — the canonical new form
* `['BC016+CR016']` — upper bound of both ranges
* `['BC001+CR001', 'BC002+CR002']` — multiple pairs on one biosample
* `['BC001', 'BC001+CR001']` — a bare barcode and a pair coexisting (also confirms `uniqueItems`
  treats them as distinct)

Add to `test_biosample_multiplexing_barcodes_invalid`:

* `['CR001+BC001']` — wrong order
* `['BC001+BC002']` — same-family pair
* `['BC001+CR017']` — out-of-range second component
* `['BC001+']` and `['+CR001']` — missing component
* `['BC001+CR001+CR002']` — more than two components
* `['BC001 + CR001']` — whitespace around the separator

## Explicitly out of scope

* No `schema_version` bump and no file under `src/igvfd/upgrade/` — the change cannot invalidate
  existing objects.
* No OpenSearch mapping regeneration — no property, calculated property, or embedding changes.
* No search config change.
* No audit change; format is enforced by the schema alone.

## Verification

```bash
./scripts/test.sh unit -- --pyargs igvfd.tests.test_types_biosample_common -q
./scripts/test.sh unit -- --pyargs igvfd.tests.test_views -k "profiles or load_workbook" -q
pre-commit run --files src/igvfd/schemas/biosample.json \
  src/igvfd/schemas/changelogs/{biosample,cell_line,organoid,primary_cell_culture,tissue}.md \
  src/igvfd/tests/data/inserts/{cell_line,organoid}.json \
  src/igvfd/tests/test_types_biosample_common.py
```

Then the full unit suite (`./scripts/test.sh unit`) before opening the PR, since the biosample mixin
is shared by four concrete types.

## File-by-file summary

| File | Change |
|---|---|
| `src/igvfd/schemas/biosample.json` | `multiplexing_barcodes` pattern + description |
| `src/igvfd/schemas/changelogs/biosample.md` | minor-change entry |
| `src/igvfd/schemas/changelogs/cell_line.md` | minor-change entry |
| `src/igvfd/schemas/changelogs/organoid.md` | minor-change entry |
| `src/igvfd/schemas/changelogs/primary_cell_culture.md` | minor-change entry |
| `src/igvfd/schemas/changelogs/tissue.md` | minor-change entry |
| `src/igvfd/tests/data/inserts/cell_line.json` | add `["BC001+CR001"]` |
| `src/igvfd/tests/data/inserts/organoid.json` | add `["BC016+CR016"]` |
| `src/igvfd/tests/test_types_biosample_common.py` | valid + invalid pair cases |
