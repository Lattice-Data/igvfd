# igfvd

`igfvd` is a Python Pyramid application for storing, modifying, retrieving, and displaying the metadata (as JSON objects) for the `IGVF` project.

# Types

The biological and experimental universe is modeled with objects (e.g. Experiments, Biosamples, Files) defined in `/types`. These objects can be linked and embedded within each other by reference, forming a graph structure.

# Schemas

Each type has an associated JSONSchema in `/schemas` that defines the properties, values, and internal depedencies (relationship between properties) of valid metadata for a type. These schema are used for validation when new metadata is POSTed or old metadata is PATCHed. Schemas are `versioned` and `upgrades` mutate existing metadata to conform to a newer version of a schema.

External archive identifiers are a cross-cutting case: the accepted `dbxrefs` patterns, which object owns each level of the NCBI/EBI/DDBJ/EGA accession hierarchy, and how a stray legacy value is handled are documented in [dbxrefs_patterns.md](dbxrefs_patterns.md).
