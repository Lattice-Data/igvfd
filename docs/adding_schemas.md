# Adding a New Schema

This document outlines all the files that need to be created or updated when adding a new schema to the project.

## Checklist for Adding a New Schema

### 1. **Schema Definition** (REQUIRED)
- **File**: `src/igvfd/schemas/{schema_name}.json`
- **Purpose**: JSON schema definition with properties, required fields, validation rules
- **Notes**: Follow the existing schema structure and include appropriate mixins

### 2. **Changelog** (REQUIRED)
- **File**: `src/igvfd/schemas/changelogs/{schema_name}.md`
- **Purpose**: Track changes to the schema over time
- **Example Content**:
  ```markdown
  ## Changelog for {schema_name}.json

  ### Schema version X

  * Initial release
  ```

### 3. **Python Type Class** (REQUIRED)
- **File**: `src/igvfd/types/{schema_name}.py`
- **Purpose**: Python class that defines the item type, loads schema, and adds calculated properties
- **Must Include**:
  - **For concrete schemas**: `@collection()` decorator with name and properties
  - **For abstract schemas**: `@abstract_collection()` decorator with name and properties
  - `item_type` attribute
  - `schema = load_schema()` call
  - `embedded_with_frame` list (if needed)
  - `summary` calculated property (recommended for concrete schemas)
- **Example Structure for Concrete Schema**:
  ```python
  from snovault import (
      collection,
      load_schema,
      calculated_property,
  )
  from snovault.util import Path
  from .base import (
      Item,
  )

  @collection(
      name='{schema_name}s',  # plural
      properties={
          'title': '{Title}s',
          'description': 'Description of the collection',
      }
  )
  class {ClassName}(Item):
      item_type = '{schema_name}'
      schema = load_schema('igvfd:schemas/{schema_name}.json')
      embedded_with_frame = [
          Path('lab', include=['@id', 'title']),
          Path('submitted_by', include=['@id', 'title']),
      ]

      @calculated_property(
          schema={
              'title': 'Summary',
              'type': 'string',
              'description': 'A summary of the item.',
              'notSubmittable': True,
          }
      )
      def summary(self, ...):
          # Implement summary logic
          pass
  ```
- **Example Structure for Abstract Schema**:
  ```python
  from snovault import (
      abstract_collection,
      load_schema,
  )
  from .base import (
      Item,
  )

  @abstract_collection(
      name='{schema_name}s',  # plural
      properties={
          'title': '{Title}s',
          'description': 'Abstract base class for {description}',
      }
  )
  class {ClassName}(Item):
      """
      Abstract base class for {description}.
      Concrete implementations are {ConcreteClass1} and {ConcreteClass2}.
      """
      item_type = '{schema_name}'
      schema = load_schema('igvfd:schemas/{schema_name}.json')
  ```

### 4. **OpenSearch Mapping** (REQUIRED)
- **File**: `src/igvfd/mappings/{schema_name}.json`
- **Purpose**: Defines how the schema is indexed in OpenSearch
- **Notes**: This is typically auto-generated using mapping generation scripts. However for new schema you would need to add `src/igvfd/mappings/{schema_name}.json` file, that subsequently will be overwritten by the script below. Before running the script, ensure the placeholder file contains the required keys so the application can boot:
  ```json
  {
      "hash": "",
      "index_name": "{schema_name}_initial",
      "item_type": "{schema_name}",
      "mapping": {}
  }
  ```
  The `index_name` value is temporary; the generator will replace it with the actual name.
- **Scripts to Run**:
  ```bash
  # Generate mapping
  docker compose down -v && docker compose build
  docker compose run pyramid /scripts/pyramid/generate-opensearch-mappings.sh
  ```

### 5. **Search Configuration** (REQUIRED)
- **File**: `src/igvfd/searches/configs/{schema_name}.py`
- **Purpose**: Defines search behavior and columns for the schema
- **Must Include**:
  - Imports from parent config classes
  - Custom columns configuration
  - Search facets (if needed)

### 6. **Test Fixtures** (REQUIRED for concrete schemas only)
- **File**: `src/igvfd/tests/fixtures/schemas/{schema_name}.py`
- **Purpose**: Pytest fixtures for creating test instances
- **Must Include**:
  - At least one basic fixture
  - Additional fixtures for edge cases (with aliases, with relationships, etc.)
- **Note**: Abstract schemas do NOT need test fixtures (concrete subclasses handle this)
- **Example**:
  ```python
  import pytest

  @pytest.fixture
  def {schema_name}(testapp, other_lab):
      item = {
          'lab': other_lab['@id'],
          # ... other required fields
          'status': 'current',
      }
      return testapp.post_json('/{schema_name}', item, status=201).json['@graph'][0]
  ```

### 7. **Test Insert Data** (REQUIRED for concrete schemas only)
- **File**: `src/igvfd/tests/data/inserts/{schema_name}.json`
- **Purpose**: Sample data loaded when spinning up a local instance
- **Notes**: Should include at least one valid example
- **Note**: Abstract schemas do NOT need test insert data (concrete subclasses handle this)
- **UUID Requirements**:
  - **CRITICAL: UUIDs must be globally unique across ALL insert files**. Duplicate UUIDs will cause "duplicate key value violates unique constraint" errors during test workbook loading.
  - Before adding new UUIDs, search existing insert files to ensure no conflicts:
    ```bash
    # Check if a UUID is already in use
    grep -r "your-uuid-here" src/igvfd/tests/data/inserts/
    ```
  - Generate **new valid UUIDs** for each new object being created. Use a UUID generator tool or Python:
    ```python
    import uuid
    print(uuid.uuid4())
    ```
  - When linking to other objects (via `linkTo` fields), use the **existing UUIDs** from those objects' insert files
  - Example: If creating a library that references a tissue sample, use the UUID from `tissue.json` insert file
  - Check existing insert files in `src/igvfd/tests/data/inserts/` to find UUIDs for linked objects

### 8. **Type Tests** (REQUIRED for concrete schemas only)
- **File**: `src/igvfd/tests/test_types_{schema_name}.py`
- **Purpose**: Unit tests for the type class
- **Should Test**:
  - Required fields validation
  - Enum validation (if applicable)
  - Pattern validation (if applicable)
  - Calculated properties (like `summary`)
  - Successful creation
  - Edge cases
- **Note**: Abstract schemas do NOT need type tests (concrete subclasses handle this)

### 9. **Update loadxl.py** (REQUIRED for concrete schemas only)
- **File**: `src/igvfd/loadxl.py`
- **Purpose**: Add schema to the loading order and pipeline phases
- **What to Do**:
  1. Add the schema name to the `ORDER` list in the appropriate position (considering dependencies)
  2. Add the schema to `PHASE1_PIPELINES` dictionary with appropriate `skip_rows_missing_all_keys` for required fields
  3. Add the schema to `PHASE2_PIPELINES` dictionary with the same `skip_rows_missing_all_keys` configuration
  4. Phase 1 uses POST method (initial creation), Phase 2 uses PUT method (updates for reference cycles)
- **Note**: Abstract schemas should NOT be added to the `ORDER` list or pipeline phases, as they are not directly instantiated
- **Example**:
  ```python
  ORDER = [
      # ... existing items ...
      'plate_based_library',
  ]

  PHASE1_PIPELINES = {
      # ... existing items ...
      'plate_based_library': [
          skip_rows_missing_all_keys('lab', 'samples'),
      ],
  }

  PHASE2_PIPELINES = {
      # ... existing items ...
      'plate_based_library': [
          skip_rows_missing_all_keys('lab', 'samples'),
      ],
  }
  ```

#### Loadxl update logic when adding linkTo

The main issue is not “rows that don’t have the link” but **rows that do have the link while the linked object is not loaded yet**. To avoid broken references, use this pattern (same as `file` with optional `derived_from`):

1. **Phase 1 (POST)**
   For any type that has optional linkTo fields: **strip** those keys in Phase 1 with `remove_keys(...)` so the initial POST does not send them. That way you never reference an object that might not exist yet.
   - Example: biosample concrete types use `remove_keys(*BIOSAMPLE_OPTIONAL_LINKTO_KEYS)` so `experimental_conditions` and `treatments` are not sent in Phase 1.

2. **Phase 2 (PUT)**
   Only process rows that **have** the optional linkTo so you can add it back: use `skip_rows_missing_all_keys(linkTo_key)` so rows **missing** that key are skipped. Phase 2 then only runs for rows that have the link; by then the linked type is already loaded (it appears earlier in `ORDER`), so the PUT is safe.
   - Example: for files, Phase 2 uses `skip_rows_missing_all_keys('derived_from')` so only rows with `derived_from` are updated. For biosample types, Phase 2 uses `skip_rows_missing_all_keys(*BIOSAMPLE_OPTIONAL_LINKTO_KEYS)` so only rows that have at least one of `experimental_conditions` or `treatments` get a PUT that adds those links back.

3. **ORDER (load order)**
   The type that is linked to must appear in `ORDER` **before** any type that references it (e.g. add `'treatment'` before biosample concrete types). That ensures Phase 2 PUTs see the linked objects already in the DB.

4. **New schema that is linked to**
   Add the new schema to `PHASE1_PIPELINES` and `PHASE2_PIPELINES` with `skip_rows_missing_all_keys` for that schema’s **required** fields only.

**Summary:** For optional linkTo: strip it in Phase 1 (`remove_keys`), then in Phase 2 only process rows that have it (`skip_rows_missing_all_keys(linkTo_key)`) and add it back via PUT. Put the referenced type earlier in `ORDER`.

### 10. **Update conftest.py** (REQUIRED for concrete schemas only)
- **File**: `src/igvfd/tests/conftest.py`
- **Purpose**: Register test fixtures so pytest can discover and use them
- **What to Do**: Add `'igvfd.tests.fixtures.schemas.{schema_name}'` to the `pytest_plugins` list
- **Note**: Abstract schemas do NOT need to be registered (concrete subclasses handle this)
- **Example**:
  ```python
  pytest_plugins = [
      # ... existing plugins ...
      'igvfd.tests.fixtures.schemas.tissue',
      'igvfd.tests.fixtures.schemas.primary_cell_culture',  # Add new schema here
  ]
  ```

---

## Summary by File Type

| File Type | Path Pattern | Required for Abstract | Required for Concrete | Auto-Generated | Notes |
|-----------|--------------|----------------------|----------------------|----------------|-------|
| Schema | `src/igvfd/schemas/{name}.json` | ✅ | ✅ | ❌ | JSON schema definition |
| Changelog | `src/igvfd/schemas/changelogs/{name}.md` | ✅ | ✅ | ❌ | Track schema changes |
| Type Class | `src/igvfd/types/{name}.py` | ✅ | ✅ | ❌ | Use `@abstract_collection` for abstract, `@collection` for concrete |
| Mapping | `src/igvfd/mappings/{name}.json` | ❌ | ✅ | ⚠️ (via script) | Only concrete schemas |
| Search Config | `src/igvfd/searches/configs/{name}.py` | ❌ | ✅ | ❌ | Only concrete schemas |
| Test Fixtures | `src/igvfd/tests/fixtures/schemas/{name}.py` | ❌ | ✅ | ❌ | Only concrete schemas |
| Test Inserts | `src/igvfd/tests/data/inserts/{name}.json` | ❌ | ✅ | ❌ | Only concrete schemas |
| Type Tests | `src/igvfd/tests/test_types_{name}.py` | ❌ | ✅ | ❌ | Only concrete schemas |
| loadxl.py | `src/igvfd/loadxl.py` | ❌ | ✅ | ❌ | Only concrete schemas |
| conftest.py | `src/igvfd/tests/conftest.py` | ❌ | ✅ | ❌ | Concrete schemas only |

---

## Common Patterns

### Schema Structure
- Use mixins from `mixins.json` for common fields (aliases, attribution, etc.)
- Define clear `required` fields
- Use `enum` for controlled vocabularies
- Use `pattern` for format validation
- Include `submissionExample` in documentation
- Set appropriate `permission` levels

### Status Field
- Most schemas use `shared_status` mixin with values: `["current", "deleted"]`

### Calculated Properties
The `summary` property is a common calculated property that provides a human-readable summary:
- Priority: aliases[0] > description > term_name > uuid
- Always marked as `notSubmittable: True`

### Test Coverage
Each schema should have tests for:
1. Summary property behavior
2. Required field validation
3. Enum field validation
4. Pattern validation
5. Successful object creation
6. Creation with all optional fields

---


## Notes and Best Practices

1. **Naming Conventions**:
   - Schema files: snake_case (e.g., `human_donor.json`)
   - Python classes: PascalCase (e.g., `HumanDonor`)
   - Collection names: plural snake_case (e.g., `human_donors`)
   - item_type: singular snake_case (e.g., `human_donor`)

2. **Abstract vs Concrete Schemas**:
   - **Abstract schemas**:
     - Use `@abstract_collection` decorator
     - Do NOT add to `loadxl.py` ORDER list
     - Do NOT create test fixtures or test data
     - Do NOT create search configuration files
     - Do NOT create mapping files (concrete implementations handle these)
     - DO create: schema JSON, changelog, type class only
     - Purpose: Define common properties/structure inherited by concrete implementations
     - Examples: `Donor`, `Biosample`, `Library`
   - **Concrete schemas**:
     - Use `@collection` decorator
     - Add to `loadxl.py` ORDER list
     - Create test fixtures and test data
     - Create search configuration files
     - Create/generate mapping files
     - DO create: all files listed in checklist
     - Examples: `HumanDonor`, `Tissue`, `SequencingLibrary`
   - Abstract schemas are base classes that define common properties but are never directly instantiated
   - Concrete schemas are actual implementations that can be instantiated and stored in the database

3. **Dependencies**:
   - If your schema references other schemas (via linkTo), ensure those schemas are loaded first in `loadxl.py`
   - If referencing an abstract schema (e.g., `linkTo: "Donor"`), ensure the abstract schema has a type class registered (even if abstract)

4. **Mixins**:
   - Reuse common property groups from `mixins.json`
   - Common mixins: `aliases`, `attribution`, `documents`, `notes`, `shared_status`

5. **Changelog**:
   - Always document what changed and why
   - Include schema version numbers

6. **Testing**:
   - Write comprehensive tests before considering the schema complete
   - Test both success and failure cases
   - Test calculated properties
   - Note: Abstract schemas don't need their own tests, but concrete implementations should test inheritance behavior

---

## Example: Adding a "Sample" Schema

If you were to add a new "sample" schema, you would create/update:

1. ✅ `src/igvfd/schemas/sample.json` - Define the schema
2. ✅ `src/igvfd/schemas/changelogs/sample.md` - Create changelog
3. ✅ `src/igvfd/types/sample.py` - Create type class
4. ✅ `src/igvfd/mappings/sample.json` - Generate mapping
5. ✅ `src/igvfd/searches/configs/sample.py` - Configure search
6. ✅ `src/igvfd/tests/fixtures/schemas/sample.py` - Create fixtures
7. ✅ `src/igvfd/tests/data/inserts/sample.json` - Add test data
8. ✅ `src/igvfd/tests/test_types_sample.py` - Write tests
9. ✅ `src/igvfd/loadxl.py` - Add to ORDER list
10. ✅ `src/igvfd/tests/conftest.py` - Register fixtures in pytest_plugins

Then run the mapping generation script and tests.
