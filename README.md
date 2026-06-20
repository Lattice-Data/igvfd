[![Tests](https://github.com/Lattice-Data/igvfd/actions/workflows/tests.yml/badge.svg)](https://github.com/Lattice-Data/igvfd/actions/workflows/tests.yml)
# igvfD
Metadata database for IGVF project.

## Run with Docker Compose
1. Clone repository and make sure Docker is running.
2. Start services and load data inserts:
```bash
# From repository.
$ docker compose up
# Note if any dependencies have changed (e.g. switching between branches that
# rely on different versions of snovault) use the build flag as well
# to rebuild the underlying Docker image:
$ docker compose up --build
```
3. Browse at `localhost:8000`.
4. Stop services and remove data volume:
```bash
$ docker compose down -v --remove-orphans
```

The dev stack uses compose project name `igvfd-dev`. Test stacks use separate project names (`igvfd-test`, `igvfd-test-indexer`) so dev data does not contaminate test postgres volumes.

## Test with Docker Compose

Use [`scripts/test.sh`](scripts/test.sh) for all local test runs. It runs preflight cleanup, executes tests, and tears down stacks automatically (including on `Ctrl+C`).

```bash
# Full unit test suite (excludes @pytest.mark.indexing)
$ ./scripts/test.sh unit

# Full indexer test suite (@pytest.mark.indexing only)
$ ./scripts/test.sh indexer

# Targeted unit tests
$ ./scripts/test.sh unit -- -k "test_foo" -q --tb=short
$ ./scripts/test.sh unit -- --pyargs igvfd.tests.test_audit_plate_based_library -q

# Targeted indexer tests
$ ./scripts/test.sh indexer -- -k "test_indexing_foo" -q

# If tests hang or ports conflict
$ ./scripts/test.sh reset

# Show running igvfd containers and port usage
$ ./scripts/test.sh status

$ ./scripts/test.sh --help
```

**Important:** `pytest.ini` sets `--pyargs igvfd.tests`. For targeted runs, `./scripts/test.sh` clears that automatically. If running pytest manually inside a container, you must pass `--override-ini addopts=` or pytest collects the **entire suite** (~1300+ tests) and appears hung. Use `--pyargs igvfd.tests.<module>` (no `.py` suffix) or `-k`.

**Indexer tests:** use `./scripts/test.sh indexer` only for tests marked `@pytest.mark.indexing`. Audit tests that use `indexer_testapp` or `@@index-data` run on the unit stack.

Requires Docker Compose v2 (same as CI).

### Interactive debugging

Prefer the wrapper shell mode (automatic cleanup on exit):

```bash
$ ./scripts/test.sh shell unit      # unit fixtures + bash in pyramid container
$ ./scripts/test.sh shell indexer   # indexer fixtures + bash in indexer-tests container
```

Advanced manual flow (unit tests):

1. Start fixtures:
```bash
$ docker compose -f docker-compose.test.yml up postgres localstack
```
2. Connect to testing environment:
```bash
$ docker compose -f docker-compose.test.yml run --rm --service-ports pyramid /bin/bash
```
3. Run tests inside the container:
```bash
$ pytest --override-ini addopts= -p igvfd.tests --pyargs igvfd.tests.test_foo -q
```
4. Stop and clean:
```bash
$ docker compose -f docker-compose.test.yml down -v --remove-orphans
```

Advanced manual flow (indexer tests):

1. Start fixtures:
```bash
$ docker compose -f docker-compose.test-indexer.yml up localstack postgres opensearch pyramid nginx invalidation-service indexing-service
```
2. Connect:
```bash
$ docker compose -f docker-compose.test-indexer.yml run --rm --service-ports indexer-tests /bin/bash
```
3. Run tests:
```bash
$ pytest -m indexing -q
```
4. Stop and clean:
```bash
$ docker compose -f docker-compose.test-indexer.yml down -v --remove-orphans
```

## Automatic linting
This repo includes configuration for pre-commit hooks. To use pre-commit, install pre-commit, and activate the hooks:
```bash
pip install pre-commit==2.17.0
pre-commit install
```
Now every time you run `git commit` the automatic checks are run to check the changes you made.


## Generate Opensearch mappings

The `igvfd-check-opensearch-mappings` test on CircleCI will fail if the mappings haven't been updated after changing schemas, calculated properties, or embedded fields.

```bash
$ ./scripts/test.sh reset
$ docker compose down -v --remove-orphans && docker compose build
$ docker compose run --rm pyramid /scripts/pyramid/generate-opensearch-mappings.sh
```

This will regenerate the mappings and allow you to see any differences with `git diff`. Commit the changes and push.

Note if you are adding a new item type, you must add a template JSON file to the `mappings/` folder with the same name as the new type (e.g. `access_key.json`). The template file requires the `index_name` and `item_type` keys, but the values can be empty:

```bash
$ echo '{"index_name": "", "item_type": ""}' > src/igvfd/mappings/new_type.json
```

Once the JSON template exists the correct values will be filled in by the `generate-opensearch-mappings.sh` script.
