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
- **Purpose**: Add schema to the loading order
- **What to Do**: Add the schema name to the `ORDER` list in the appropriate position (considering dependencies)
- **Note**: Abstract schemas should NOT be added to the `ORDER` list, as they are not directly instantiated

### 10. **Update conftest.py** (IF NEEDED)
- **File**: `src/igvfd/tests/conftest.py`
- **Purpose**: Register test types if they need special handling

---

## Summary by File Type

| File Type | Path Pattern | Required | Auto-Generated | Notes |
|-----------|--------------|----------|----------------|-------|
| Schema | `src/igvfd/schemas/{name}.json` | ✅ | ❌ | Both abstract and concrete |
| Changelog | `src/igvfd/schemas/changelogs/{name}.md` | ✅ | ❌ | Both abstract and concrete |
| Type Class | `src/igvfd/types/{name}.py` | ✅ | ❌ | Use `@abstract_collection` for abstract, `@collection` for concrete |
| Mapping | `src/igvfd/mappings/{name}.json` | ✅ | ⚠️ (via script) | Both abstract and concrete |
| Search Config | `src/igvfd/searches/configs/{name}.py` | ✅ | ❌ | Both abstract and concrete |
| Test Fixtures | `src/igvfd/tests/fixtures/schemas/{name}.py` | ✅ | ❌ | Concrete schemas only |
| Test Inserts | `src/igvfd/tests/data/inserts/{name}.json` | ✅ | ❌ | Concrete schemas only |
| Type Tests | `src/igvfd/tests/test_types_{name}.py` | ✅ | ❌ | Concrete schemas only |
| loadxl.py | `src/igvfd/loadxl.py` | ✅ | ❌ | Concrete schemas only |

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
   - **Abstract schemas**: Use `@abstract_collection` decorator, do NOT add to `loadxl.py` ORDER list, do NOT create test fixtures or test data (concrete subclasses handle this)
   - **Concrete schemas**: Use `@collection` decorator, add to `loadxl.py` ORDER list, create test fixtures and test data
   - Abstract schemas are base classes that define common properties but are never directly instantiated (e.g., `Donor`, `Biosample`)
   - Concrete schemas are actual implementations that can be instantiated (e.g., `HumanDonor`, `Tissue`)

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

Then run the mapping generation script and tests.
