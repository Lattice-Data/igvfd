# igvfd — agent instructions

## Tests (Docker only)

Always use [`scripts/test.sh`](scripts/test.sh) for tests. **Never** run `pytest` on the host or bare `docker compose` for test runs.

```bash
./scripts/test.sh unit                              # full unit suite
./scripts/test.sh indexer                           # full indexer suite
./scripts/test.sh unit -- --pyargs igvfd.tests.test_foo -q   # targeted module
./scripts/test.sh unit -- -k "test_name" -q         # targeted by expression
./scripts/test.sh reset                             # if hung or ports conflict
./scripts/test.sh --help
```

## pytest.ini trap

`pytest.ini` sets `--pyargs igvfd.tests`. Passing another `--pyargs` on the CLI does **not** replace it — pytest collects the **entire suite** (~1300+ tests) and appears hung.

`./scripts/test.sh` clears addopts automatically for targeted runs. Manual pytest must use:

```bash
pytest --override-ini addopts= -p igvfd.tests --pyargs igvfd.tests.test_foo -q
```

## Unit vs indexer

| Stack | When |
|-------|------|
| `./scripts/test.sh unit` | Default — schema, audit, type, upgrade tests; includes `indexer_testapp` / `@@index-data` audit tests |
| `./scripts/test.sh indexer` | **Only** tests marked `@pytest.mark.indexing` |

Indexer stack starts 7+ services and can take 5+ minutes on cold start. Do not use it unless the test file has `@pytest.mark.indexing`.

## OpenSearch mappings (after schema changes)

See README "Generate Opensearch mappings". Run `./scripts/test.sh reset` first if Docker stacks may be stale.

## Troubleshooting

- No output for 3+ minutes after starting tests: run `./scripts/test.sh reset` and retry once.
- First cold Docker start often takes 2–5 minutes — that is normal.
- Report exact command and last 30 lines of output if still stuck.

Full details: [README.md](README.md), [.cursor/rules/docker-testing.mdc](.cursor/rules/docker-testing.mdc).
