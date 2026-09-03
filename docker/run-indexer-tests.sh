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
# Usage: ./docker/run-indexer-tests.sh [--no-build]
#
#   --no-build   Skip the image build. For callers that have already built the
#                images, such as CI, which builds them up front with a shared
#                layer cache; rebuilding inside compose would bypass that cache.
#
set -euo pipefail

cd "$(dirname "$0")/.."

# A plain string, not an array: under `set -u`, bash 3.2 -- still the default on
# macOS -- treats "${empty_array[@]}" as an unbound variable and aborts. Word
# splitting on an empty string expands to no argument, which is what is wanted here
# and matches how $COMPOSE below is expanded.
BUILD_ARG="--build"
if [[ "${1:-}" == "--no-build" ]]; then
    BUILD_ARG=""
    shift
fi
if [[ $# -gt 0 ]]; then
    echo "usage: $0 [--no-build]" >&2
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
