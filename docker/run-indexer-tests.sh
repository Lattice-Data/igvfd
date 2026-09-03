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
# Usage: ./docker/run-indexer-tests.sh [--no-rebuild]
#
#   --no-rebuild  Do not force a rebuild of images that already exist. For callers
#                 that have already built them, such as CI, which builds them up
#                 front with a shared layer cache; forcing a rebuild inside compose
#                 would bypass that cache. Note this is not compose's --no-build:
#                 `up` still builds any image that is missing locally, which is
#                 deliberate, since failing outright on a missing image would be
#                 worse than building it.
#
set -euo pipefail

cd "$(dirname "$0")/.."

# A plain string, not an array: under `set -u`, bash 3.2 -- still the default on
# macOS -- treats "${empty_array[@]}" as an unbound variable and aborts. Word
# splitting on an empty string expands to no argument, which is what is wanted here
# and matches how $COMPOSE below is expanded.
BUILD_ARG="--build"
if [[ "${1:-}" == "--no-rebuild" ]]; then
    BUILD_ARG=""
    shift
fi
if [[ $# -gt 0 ]]; then
    echo "usage: $0 [--no-rebuild]" >&2
    exit 2
fi

COMPOSE="docker compose -p igvfd-indexer-tests -f docker-compose.test-indexer.yml"

cleanup() {
    $COMPOSE down -v --remove-orphans
}
trap cleanup EXIT

# Clear any residue from a previous (possibly interrupted) run up front.
$COMPOSE down -v --remove-orphans

# --abort-on-container-exit tears the whole stack down as soon as tests finish;
# --exit-code-from surfaces the real pytest pass/fail as this script's exit code.
# shellcheck disable=SC2086  # BUILD_ARG must word-split: empty means "no flag".
$COMPOSE up $BUILD_ARG --abort-on-container-exit --exit-code-from indexer-tests
