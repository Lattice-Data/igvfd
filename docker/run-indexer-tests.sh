#!/usr/bin/env bash
#
# Run the indexing test suite in a clean, isolated Docker Compose stack.
#
# Local re-runs of the indexer stack repeatedly failed because containers,
# anonymous volumes (stale OpenSearch/Postgres state), and networks from a
# previous run were left behind. This wrapper guarantees a clean slate before
# and after every run, and uses a dedicated project name so its containers,
# volumes and networks never collide with a dev stack (docker-compose.yml).
#
# Host ports are not project-scoped, so a *running* dev stack still conflicts:
# docker-compose.yml publishes 4566, 5432, 6543, 8000 and 9200, which covers
# every port this stack needs. Stop it first.
#
# Usage: ./docker/run-indexer-tests.sh [--no-rebuild]
#
#   --no-rebuild  Drop compose's --build, so images that are already present are
#                 not rebuilt from scratch. Note what this does *not* mean: it is
#                 not compose's --no-build, and it does not guarantee no build
#                 happens. `up` still builds anything missing locally -- which is
#                 deliberate, since failing outright on a missing image would be
#                 worse. In CI the prebuild steps use build-push-action with the
#                 docker-container driver and no `load: true`, so the images never
#                 reach the runner's image store and compose does build all of
#                 them; what the prebuild buys there is a warm buildkit cache, not
#                 image reuse.
#
set -euo pipefail

cd "$(dirname "$0")/.."

# A plain string, not an array: under `set -u`, bash 3.2 -- still the default on
# macOS -- treats "${empty_array[@]}" as an unbound variable and aborts. Word
# splitting on an empty string expands to no argument, which is what is wanted here
# and matches how $COMPOSE below is expanded.
UP_BUILD_FLAG="--build"
if [[ "${1:-}" == "--no-rebuild" ]]; then
    UP_BUILD_FLAG=""
    shift
fi
if [[ $# -gt 0 ]]; then
    echo "usage: $0 [--no-rebuild]" >&2
    exit 2
fi

COMPOSE="docker compose -p igvfd-indexer-tests -f docker-compose.test-indexer.yml"

cleanup() {
    # `|| true`: this runs in an EXIT trap under `set -e`, so without it a failing
    # teardown would replace pytest's exit status and turn a green run red.
    $COMPOSE down -v --remove-orphans || true
}
trap cleanup EXIT

# Clear any residue from a previous (possibly interrupted) run up front.
$COMPOSE down -v --remove-orphans

# --abort-on-container-exit tears the whole stack down as soon as tests finish;
# --exit-code-from surfaces the real pytest pass/fail as this script's exit code.
# shellcheck disable=SC2086  # UP_BUILD_FLAG must word-split: empty means "no flag".
$COMPOSE up $UP_BUILD_FLAG --abort-on-container-exit --exit-code-from indexer-tests
