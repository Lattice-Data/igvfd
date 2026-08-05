Adding audits
=========================

This document describes how to add and update audits that check metadata consistency and integrity.

Guide to where to edit Source Code
----------------

* **src** directory - contains all the python and javascript code for front and backends
    * **audit** - python instructions for checking metadata stored in the schema
    * **schemas** - JSON schemas ([JSONSchema], [JSON-LD]) describing allowed types and values for all metadata objects
    * **tests** - Unit and integration tests
    * **types** -  business logic for dispatching URLs and producing the correct JSON
    * **upgrade** - python instructions for upgrading old objects stored to the latest
    * **loadxl.py** - python script that defines the schema objects to load

-----

Adding a new aduit
----------------

1. To add a new audit, navigate to the *audit** directory. Determine what metadata is needed to implement the consistency and integrity check. This helps to determine which object has the appropriate metadata available and where to place the new audit. In the directory make a new python file or edit an exisiting python file named after the determined object. The file name is a convenience only; the type passed to `@audit_checker` in step 5 is what the audit actually runs against and what the audit documentation page groups by (see step 6).

2. Make a new audit definition, using the metadata needed as a guide to fall into one these 2 categories:

    * *Contained in an object* - all metadata need for audit are properties of the object where embedded
objects referred to by an identifier:

        def audit_new_audit_name(value, system):
            pass

    * *Requires metadata in other objects* - metadata need for audit are properties of the object as well as properties within embedded objects:

        def audit_new_audit_name(value, system):
            pass

3. Define the description for the audit. The description should serve to describe what type of metadata is audited in a human-readable format without any technical language, e.g. referencing of properties or object names should be in sentence case. Ideally, the description should be kept in the positive as much as possible and limited to a single sentence.

Additionally, decide on an appropriate ```AuditFailure``` category name for the audit. This category will be displayed on the faceted search. The category should be concise, precise, and avoid redundant language (e.g., use of "metadata" or "associated" since they are implied). Generally, audits will fall into one of the following three types of categories. Additional categories for special cases may be created by discretion of the wrangler. ex. `NTR term ID`.

    * a missing property or link -> "missing {property}/{item}"
    * an inconsistency with an expectation of metadata on linked item(s) -> "inconsistent {item} {property}"
    * a property or link to a type that isn't expected -> "unexpected {property}/{type}

Also determine which of the following 4 levels of severity (ERROR, NOT_COMPLIANT, WARNING, INTERNAL_ACTION) the audit should fall into. Please refer to the [audits page](https://data.igvf.org/audits/) for defintions of severity levels.

The description, category, and level should be listed in the docstring of the audit function shown as following. The docstring for each audit is used to build a row in the audit documentation page for the respective type. The docstring should be defined in JSON format.
    '''
        [
            {
                "audit_description": "Description of the audit."
                "audit_category": "Category of the audit."
                "audit_level": "Level of the audit."
            }
        ]
    '''

4. Write the logic for the metadata check and define the details to be displayed with the audit. Details should explain the discrepancy and display the values for the metadata properties that are resulting in the AuditFailure. Details should try to avoid reiterating the audit description unless necessary, since the description is displayed as well in the audit.

    Example of a ```measurement_set``` which has a preferred assay title that does not correspond to its assay term:

        from .formatter import get_audit_message

        audit_message = get_audit_message(<an_audit_function_name>, index=<int>)

        if preferred_assay_title and preferred_assay_title not in assay_object.get('preferred_assay_titles', []):
            detail = (
                f'Measurement set {audit_link(path_to_text(value["@id"]),value["@id"])} has '
                f'assay term "{assay_term_name}", but preferred assay title "{preferred_assay_title}", '
                f'which is not an expected preferred assay title for this assay term.'
            )
            yield AuditFailure(audit_message.get('audit_category', ''),
                               f'{detail} {audit_message.get("audit_description", "")},
                               level=audit_message.get('audit_level', '')
            )

    Use ```audit_link``` to format links so that the front end can find and present them. The first parameter is the text to display for the link, while the second is the link path. You must import ```audit_link``` from the .formatter library.

    The .formatter library also includes a ```path_to_text``` utility to help generate link text if all you have is the ```@id```. Pass this ```@id``` to ```path_to_text``` and it returns just the accession portion as text that you can use as link text.

5. After writing the audit function add it to the function dispatcher located at the bottom of the audit script for its respective type and frame.

6. There is nothing to register. `make-audit-docstring-json` discovers every module in `src/igvfd/audit/` automatically and reads the registered audit checkers, so a new audit module is picked up as soon as its function is added to a dispatcher. `EXCLUDED_MODULES` in `src/igvfd/commands/make_audit_docstring_json.py` is the only opt-out, and it exists for `item.py`, which audits the abstract `Item` type.

    What *does* matter is the type you pass to `@audit_checker`, because the audit documentation page groups audits by that type. The type must be one the page can render: it needs its own schema with `identifyingProperties`, or it needs child types. `Item` does not qualify. The audit module's **file name has no effect on the page** — name the file for whatever reads best.

    `test_commands_make_audit_docstring_json.py` enforces this, so an audit registered against a type the page cannot render fails the test suite rather than silently disappearing from the page. Run those tests with:

        docker compose -f docker-compose.test.yml run --rm --no-deps pyramid pytest -m 'not indexing' -k make_audit_docstring_json

    To see the generated file, generate and inspect it in a single container. The pyramid services shadow `src/igvfd/static` with an anonymous volume, so the output does not reach your checkout and a second container would show the image's older copy:

        docker compose -f docker-compose.test.yml run --rm --no-deps pyramid sh -c 'make-audit-docstring-json && python -m json.tool src/igvfd/static/doc/auditdoc.json'

    The command prints the audit count and the types it emitted; confirm your audit is listed with the type you expect. The same summary line appears in `docker build` output, since the image build regenerates the file. After rebuilding, bring the stack up with `docker compose up -V` — Compose reuses that anonymous volume by default, which can otherwise keep serving the previous `auditdoc.json`.

7. In the **tests** directory add audit test to an existing/new python file named ```test_audit_{metadata_object}.py```. This example shows the basic structure of setting up ```pytest.fixture``` and test that ```property_1``` is present if ```property_2``` is RNA:

        @pytest.fixture
        def {metadata_object}_1:
            item = {
                'property_2': 'RNA',
            }
            return testapp.post_json('/{metadata_object}', item, status=201).json['@graph'][0]


        def test_{metadata_object}_property_1(testapp, {metadata_object}_1):
            res = testapp.get({metadata_object}_1['@id'] + '@@index-data')
                errors = res.json['audit']
                errors_list = []
                for error_type in errors:
                    errors_list.extend(errors[error_type])
                assert any(error['category'] == 'missing prperty 1' for error in errors_list)
