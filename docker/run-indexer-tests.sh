#!/usr/bin/env bash
#
# Run the indexing test suite in a clean, isolated Docker Compose stack.
#
# Local re-runs of the indexer stack repeatedly failed because containers,
# anonymous volumes (stale OpenSearch/Postgres state), and networks from a
# previous run were left behind. This wrapper guarantees a clean slate before
# and after every run, and uses a dedicated project name so it never collides
# with a running dev stack (docker-compose.yml).
#
# Usage: ./docker/run-indexer-tests.sh
#
set -euo pipefail

cd "$(dirname "$0")/.."

COMPOSE="docker compose -p igvfd-indexer-tests -f docker-compose.test-indexer.yml"

cleanup() {
    $COMPOSE down -v --remove-orphans
}
trap cleanup EXIT

# Clear any residue from a previous (possibly interrupted) run up front.
$COMPOSE down -v --remove-orphans

# --abort-on-container-exit tears the whole stack down as soon as tests finish;
# --exit-code-from surfaces the real pytest pass/fail as this script's exit code.
$COMPOSE up --build --abort-on-container-exit --exit-code-from indexer-tests
