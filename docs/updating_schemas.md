Making changes to schemas
=========================

This document describes how to make changes to the JSON schemas ([JSONSchema], [JSON-LD]) and source code that describes the encoded metadata model. For overview of code organization see [overview.md](https://github.com/IGVF-DACC/igvfd/blob/dev/docs/overview.md).

Guide to where to edit Source Code
----------------

* **src/igvfd** Directory - contains all the Python code for backends needs
    * **/audits** - Contains Python scripts that are run post-submission to check JSON objects' metadata stored in the schema
    * **/schemas** - JSON schemas ([JSONSchema], [JSON-LD]) describing allowed types and values for all metadata objects
      * **/schemas/changelogs** - Schema change logs for documenting the changes made in each version of a schema
      * **/schemas/mixins.json** - Common schema property definitions for use with multiple schemas
    * **/tests** - Unit and integration tests
      * **/tests/data/inserts** - The sample data that comes up in a basic local instance.
      * **/tests/fixtures/schemas** - The sample Python objects to use with unit tests.  These Python function names are used as parameters in unit tests.
    * **/types** -  Logic for dispatching URLs and producing the correct JSON.  This is where computed fields are specified.
    * **/upgrade** - Python instructions for upgrading old objects to match the new schema
    * **/loadxl.py** - Python script that defines the schema objects to load
    * **/schema_format.py** - The format checker for accessions
    * **/searches** - Directory that contains the configurations for search results
      * **/searches/defaults.py** - This file contains a list that determines if a new schema is searched by default
      * **/searches/configs** - Directory that has a file for each type that contains the list of fields returned in a search

Adding a new schema
----------------
Follow the checklist in `docs/adding_schemas.md`.


-----

Schema property guidelines
----------------

* When naming a property, try to avoid overly long names.
* Array properties must have a plural property name: samples, not sample.

Below are the required and optional components divided according the property's `type`.
* All properties:
    * `title`: Required. A readable name of the property, in Title Case.
    * `type`: Required. `string`, `number`, `integer`, `boolean`, `array`, or `object`.
    * `description`: Required. A definition of the property.
    * `default`: A default value automatically assigned if no value is provided upon submission.
    * Strings:
        * `enum`: A list of valid values when a property requires a controlled vocabulary.
        * `linkTo`: A list of valid objects to link to. Must be the name of a schema, which can be abstract or concrete.
        * `pattern`: A regex pattern applied to the string.
    * Numbers or integers:
        * `minimum`: A minimum value.
        * `maximum`: A maximum value.
    * Arrays:
        * `items`: Required. A definition of the items that are valid in the array. Must include `type` at minimum.
        * `minItems`: Required. An integer indicating the minimum number of items in an array. Must be at least 1.
        * `maxItems`: An integer indicating the maximum number of items in an array.
        * `uniqueItems`: Required. A boolean which is always `True`.
    * Objects:
        * `properties`: A nested schema. Must obey above requirements for each property: `title`, `type`, and `description`.

The following are properties categorized by the feasibility to submit. These properties must follow the preceding guidelines according to their `type` in addition to the guidelines below.
* Submittable properties:
    * `comment`: Instructions for submitters explaining details of how to submit the property. If there is a dependency defined for the property, the comment must include: "This property is affected by dependencies. See \[link\]."
    * `submissionExample`: Required. An example of how to specify the property using appscript and igvf_utils tools.
* Admin only properties:
    * `permission`: Required. A string property which is always `admin_only`. Must not be present for any property that can be modified by any submitter.
* Calculated properties:
    * `notSubmittable`: Required. A boolean property which is always `True`. Must not be present for any submittable property.

-----

Changelog guidelines
----------------

* Do record changes in calculated properties.
* Don't record changes to searches, such as fuzzy vs. exact, or to embedding.
* Add entries to all affected schemas when there is a change to properties which are inherited or merged into other schemas, such as mixins.
* Add new entries at the top of the changelog.
* Record changes occurring in different PRs as separate entries.
* Mention only one property per line. Additionally, only one enum should be mentioned in a line where possible. For example, if 10 enums are added to a property, each one is noted on a separate line.
* Begin with a present tense verb describing the action: add, remove, rename. Adhere to the stylebook whenever possible.


### Stylebook
The following table provides common types of schema changes and provides a specific sentence pattern to follow for the entry.
|Type of schema change|Sentence example|
|-|-|
|Add a property|Add \[property name\].|
|Remove a property|Remove \[property name\].|
|Replace a property|Rename \[old name\] to \[new name\].|
|Add an enum|Extend \[property name\] enum list to include \[enum\].|
|Remove an enum|Reduce \[property name\] enum list to exclude \[enum\].|
|Replace an enum|Adjust \[property name\] enum list to replace \[old enum\] with \[new enum\].|
|Restrict an enum to admins|Adjust \[property name\] enum list to restrict usage of \[deprecated term\] to admin users.|
|Relax an enum to any user|Adjust \[property name\] enum list to allow usage of \[deprecated term\] by all users.|
|Change a regex|Update \[property name\] regex to \[description of regex\].|
|Add or change a dependency or requirement|Require \[description of requirement\].|
|Add a calculated property|Add calculated property \[property name\].|
|Remove a calculated property|Remove calculated property \[property name\].|
|Change a calculated property|Update the calculation of \[property name\].|

-----

Updating an existing schema
----------------

There are two situations we need to consider when updating an existing schema: (1) No update of the schema version (2) Update schema version

**When not to update a version**

* Do not update the schema version if the updated schema allows all existing objects in the database to continue to validate. For example, a new enum value in an existing list of enums would not cause existing objects of that type to fail validation.

**NOTE:**
Exception: When making substantial changes to an existing schema, even if these changes do not cause the existing objects using this schema to fail validation, an update is recommended (please see below).

**When to update a version**

* Schema version has to be updated (bumped up by 1) if the change that is being introduced will lead to a potential invalidation of existing objects in the database.

* Examples include:
    1) Changing the name of a property in the existing schema.
    2) Removing a property from the existing schema.
    3) A property that previously allowed free text is now changed to a possible list of allowed enums.
    4) Removing an enum from an existing property.

* Most of the cases described above are examples where existing objects could potentially fail the validation under the new schema version. Hence, an additional step of adding an upgrade script is required. This will ensure that all the existing objects will be upgraded (changed) such that they will be valid under the new schema version.

* **NOTE:** You should update the schema version when making substantial changes to an existing schema even if these changes do not cause existing objects using this schema to fail validation.
The new schema version number in such cases helps submitters and users realize that a substantial change has been made to the schema and they may need to update their scripts accordingly.

* **NOTE:** You should also update the appropriate changelog markdown file with documentation of the new schema version, in `src/igvfd/schemas/changelogs/`. You should update the changelog even if the schema version number has not been bumped up. If so, it appears as "minor changes since schema version xyz".

* **NOTE:** Whenever in doubt (whether to update or not), it would be a good idea to discuss with other members of the group as there can be grey areas as mentioned in the note above. When multiple new properties are being added to the new schema (potentially leading to no conflict with the schema validation), technically the upgrade step would just be bumping the schema version.

**Some detailed steps to follow in each of the above cases are outlined below**

### No update of the schema version

1. In `src/igvfd/schemas/`, edit the existing properties in the corresponding JSON file named after the object.

2. In `src/igvfd/types/`, make appropriate updates to object class by adding *embedding*, *reverse links*, and *calculated properties* as necessary.

3. If applicable, update the search config in `src/igvfd/searches/configs/{type}.py` (e.g. when changing fields that should appear as columns/facets in search results).

4. Update the inserts within `src/igvfd/tests/data/inserts/`.

5. Add test in `src/igvfd/tests/` to make sure your schema change functions as expected.

**Specific example from the treatment object schema change:**
For example, if we included a minor change in treatment object such that *μg/kg* could be specified as treatment units, the following test should allow one to test whether the update has been successfully implemented or not:

        def test_treatment_patch_amount_units(testapp, treatment):
            testapp.patch_json(
            treatment['@id'],
            {
                'treatment_type': 'injection',
                'amount': 20,
                'amount_units': 'μg/kg'
            },
            status=200,
            ## Status 200 means the object was successfully patched and the schema update works as expected.
        )

6. If applicable, regenerate OpenSearch mappings after changes to schemas, calculated properties, or embedded fields (see `README.md` "Generate Opensearch mappings"):

```bash
docker compose down -v && docker compose build
docker compose run pyramid /scripts/pyramid/generate-opensearch-mappings.sh
```

7. Document the changes to the corresponding log file within `src/igvfd/schemas/changelogs/`.

**Specific example from the treatment object schema change:**
For example, a minor change in the treatment object after version 11 that allowed one to use *μg/kg* as treatment amount units is shown below:

        ### Minor changes since schema version 11

        * *μg/kg* can now be specified as amount units.

### Update schema version

1. In `src/igvfd/schemas/`, edit the existing properties in the corresponding JSON file named after the object and increment the schema version.

**Specific example from the genetic modifications object schema change:**

Up until schema version 6 for the genetic modifications object, "validation" was an enum for the "purpose" property. As a part of schema version update to 7, "validation" was removed and instead the term "characterization" was added.


        "purpose":{
            "title": "Purpose",
            "description": "The purpose of the genetic modification.",
            "type": "string",
            "enum": [
                "activation",
                "validation",
                "expression"
            ]
        },

Replacing the enum "validation" by the enum "characterization" in the list of enums of the "purpose" property:

        "purpose":{
            "title": "Purpose",
            "description": "The purpose of the genetic modification.",
            "type": "string",
            "enum": [
                "activation",
                "characterization",
                "expression"
            ]
        },

2. In `src/igvfd/schemas/`, edit the properties in the corresponding JSON file named after the object and increment the schema version.

**Specific example from the genetic modifications object upgrade:**

For example if the original schema version for the genetic modification object being modified was "6", change it to "7" (6->7):

        "schema_version": {
            "default": "7"
        }

3. In `src/igvfd/upgrade/` add an `upgrade_step` to a python file named after the object (create new if there is no such a file in the upgrade directory). For some objects the upgrade is defined in the parent class - like dataset.py for the experiment object.

**Specific example from the genetic modifications object upgrade:**

An example to the upgrade step is shown below. Continuing with our example on genetic modifications, all the existing objects with that had "purpose" specified to be "validation" must now be changed to "characterization".

        @upgrade_step('genetic_modification', '6', '7')
        def genetic_modification_6_7(value, system):
            if value['purpose'] == 'validation':
                value['purpose'] = 'characterization'

4. In `src/igvfd/tests/data/inserts/`, we will need to change all the corresponding objects to follow the new schema.

**Specific example from the genetic modifications object upgrade:**

Continuing with our example, all the ```"purpose": "validation"``` must now be converted to ```"purpose": "characterization"```. Change all the corresponding inserts within the genetic modifications object. For example:

#genetic_modification insert **before** the change from schema version 6 to 7:

        "purpose": "validation",


#genetic_modification insert **after** the change from schema version 6 to 7:

        "purpose": "characterization",


5. Next, add an upgrade test to an existing python file named `test_upgrade_{metadata_object}.py`. If a corresponding test file doesn't exist, create a new file.

6. If applicable, update the search config in `src/igvfd/searches/configs/{type}.py` (e.g. when changing fields that should appear as columns/facets in search results).

7. If applicable, regenerate OpenSearch mappings after changes to schemas, calculated properties, or embedded fields (see `README.md` "Generate Opensearch mappings"):

```bash
docker compose down -v && docker compose build
docker compose run pyramid /scripts/pyramid/generate-opensearch-mappings.sh
```

**Specific example from the genetic modifications object upgrade:**

Below, is an example of an upgrade step that must be added to the ```test_upgrade_genetic_modification.py``` script.

        def test_genetic_modification_upgrade_6_7(upgrader, genetic_modification_6):
            value = upgrader.upgrade('genetic_modification', genetic_modification_6,
                             current_version='6', target_version='7')
            assert value['schema_version'] == '7'
            assert value.get('purpose') == 'characterization'

8. You must check the results of your upgrade on the current database:

   **Note** it is possible to write a "bad" upgrade that does not prevent your objects from loading or being shown.

   You can check using the following methods:
   * Checking for errors in the /var/log/cloud-init-output.log (search for "batchupgrade" a few times) in any demo with your upgrade, this can be done about 30min after launch (after machine reboots post-install), no need to wait for the indexing to complete.
   * Looking at the JSON for an object that should be upgraded by checking it's schema_version property.
   * Updating and object and looking in the /var/log/apache2/error.log for stack traces.

   A good upgrade would ensure that all objects POSTed before and after release would not fail validation. Nevertheless, it will be a good idea to check that again during the release.

**Specific example from a successful batch upgrade on a demo:**

You can find upgrade results on a demo at `/var/log/cloud-init-output.log`. Batchupgrade is almost the last step of demo initiation. So you would expect upgrade results at the end of that log. Batchupgrade log starts with the following progress log which is about 1300 lines:
```
INFO [snovault.batchupgrade][MainThread] Start Upgrade with 1272190 items: 1000, 1, 16, 1
INFO [snovault.batchupgrade][MainThread] 1 of ~1272 Batch: Updated 0 of 1000 (errors 0)
INFO [snovault.batchupgrade][MainThread] 2 of ~1272 Batch: Updated 0 of 1000 (errors 0)
INFO [snovault.batchupgrade][MainThread] 3 of ~1272 Batch: Updated 0 of 1000 (errors 0)
...
INFO [snovault.batchupgrade][MainThread] 1271 of ~1272 Batch: Updated 0 of 1000 (errors 0)
INFO [snovault.batchupgrade][MainThread] 1272 of ~1272 Batch: Updated 0 of 1000 (errors 0)
INFO [snovault.batchupgrade][MainThread] 1273 of ~1272 Batch: Updated 0 of 1000 (errors 0)
INFO [snovault.batchupgrade][MainThread] End Upgrade
```

After that you will find a summary of the upgrade which should indicate any potential errors. Since, in the example below, the line ```Sum errors: 0```, everything looks good for this upgrade:

```
INFO [snovault.batchupgrade][MainThread] Upgrade Summary
INFO [snovault.batchupgrade][MainThread] Sum updated: 2
INFO [snovault.batchupgrade][MainThread] Collection cart: Updated 2 of 142 (errors 0)
INFO [snovault.batchupgrade][MainThread] Collection user: Updated 616 of 616 (errors 0)
INFO [snovault.batchupgrade][MainThread] Sum errors: 0
INFO [snovault.batchupgrade][MainThread] Run Time: 11.91 minutes
```
If you do see any errors in the summary above, you must to look at log above and find out what objects failed the upgrade and why.

9. If applicable you may need to update audits on the metadata. Please refer to [making_audits]

10. To document all the schema changes that occurred between increments of the `schema_version` update the object changelogs in `src/igvfd/schemas/changelogs/`.

**Specific example from the genetic modifications object upgrade:**

Continuing with our example of upgrading genetic modifications object, the changelog for this upgrade would look like the following:

        ### Schema version 7

        * *purpose* property enum value *validation* was renamed to *characterization*



[JSONSchema]: http://json-schema.org/
[JSON-LD]:  http://json-ld.org/
[overview.rst]: overview.rst
[object-lifecycle.rst]: object-lifecycle.rst
[making_audits]: making_audits.md
