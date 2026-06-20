#!/usr/bin/env bash
# igvfd Docker test wrapper — preflight cleanup, automatic teardown, single entry point.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

COMPOSE_DEV="docker-compose.yml"
COMPOSE_UNIT="docker-compose.test.yml"
COMPOSE_INDEXER="docker-compose.test-indexer.yml"

# Legacy project name (pre name: isolation) plus current compose project names.
PROJECTS=(igvfd igvfd-dev igvfd-test igvfd-test-indexer)
CONTAINER_NAME_FILTERS=(igvfd igvfd-dev igvfd-test igvfd-test-indexer)

COMPOSE_FILE=""
KEEP_VOLUMES=false
DO_PREFLIGHT=true
DO_BUILD=false
TEARDOWN_DONE=false
START_TIME=$SECONDS
PYTEST_ARGS=()
PYTEST_CMD=()

usage() {
    cat <<'EOF'
Usage: ./scripts/test.sh <command> [options] [-- pytest-args...]

Commands:
  unit              Run full unit test suite (excludes @pytest.mark.indexing)
  indexer           Run full indexer test suite (@pytest.mark.indexing only)
  shell unit        Interactive bash in unit test stack
  shell indexer     Interactive bash in indexer test stack
  reset             Stop all igvfd compose stacks and remove volumes
  status            Show igvfd-related containers and port usage

Options:
  --build           Pass --build to docker compose up
  --no-preflight    Skip preflight cleanup (debug only; not recommended)
  --keep-volumes    Teardown without removing volumes (debug only)
  -h, --help        Show this help

Examples:
  ./scripts/test.sh unit
  ./scripts/test.sh unit -- -k "test_foo" -q --tb=short
  ./scripts/test.sh unit -- --pyargs igvfd.tests.test_audit_plate_based_library -q
  ./scripts/test.sh indexer -- -k "test_indexing_foo" -q
  ./scripts/test.sh reset
  ./scripts/test.sh status

Notes:
  - Preflight cleanup runs automatically before every test command.
  - Targeted runs clear pytest.ini addopts automatically (otherwise pytest collects
    the entire ~1300+ test suite and appears hung).
  - Use --pyargs igvfd.tests.<module> (no .py suffix) or -k for targeted runs.
  - Use indexer mode only for tests marked @pytest.mark.indexing.
EOF
}

log() {
    echo "[test.sh] $*"
}

warn() {
    echo "[test.sh] WARNING: $*" >&2
}

preflight_cleanup() {
    log "Preflight: stopping all igvfd compose stacks and removing volumes..."
    local project compose_file
    for project in "${PROJECTS[@]}"; do
        for compose_file in "$COMPOSE_DEV" "$COMPOSE_UNIT" "$COMPOSE_INDEXER"; do
            docker compose -p "$project" -f "$compose_file" down -v --remove-orphans 2>/dev/null || true
        done
    done
    # Also tear down using compose file name: (current layout).
    docker compose -f "$COMPOSE_DEV" down -v --remove-orphans 2>/dev/null || true
    docker compose -f "$COMPOSE_UNIT" down -v --remove-orphans 2>/dev/null || true
    docker compose -f "$COMPOSE_INDEXER" down -v --remove-orphans 2>/dev/null || true

    local filter
    for filter in "${CONTAINER_NAME_FILTERS[@]}"; do
        docker ps -aq --filter "name=${filter}" | xargs docker rm -f 2>/dev/null || true
    done
    log "Preflight complete."
}

check_ports() {
    if command -v lsof >/dev/null 2>&1; then
        local port_info
        port_info="$(lsof -i :4566 -i :5432 -i :6543 -i :8000 -i :9200 2>/dev/null || true)"
        if [ -n "$port_info" ]; then
            warn "Ports still in use after preflight cleanup:"
            echo "$port_info"
            warn "Run ./scripts/test.sh reset or stop the process holding these ports."
        fi
    fi
}

teardown() {
    if [ "$TEARDOWN_DONE" = true ] || [ -z "$COMPOSE_FILE" ]; then
        return 0
    fi
    TEARDOWN_DONE=true
    local down_args=(down --remove-orphans)
    if [ "$KEEP_VOLUMES" = false ]; then
        down_args+=(-v)
    fi
    log "Teardown: docker compose -f $COMPOSE_FILE ${down_args[*]}"
    docker compose -f "$COMPOSE_FILE" "${down_args[@]}" 2>/dev/null || true
}

on_exit() {
    local exit_code=$?
    teardown
    local elapsed=$((SECONDS - START_TIME))
    if [ "$exit_code" -ne 0 ] && [ -n "${COMMAND:-}" ] && [ "$COMMAND" != "reset" ] && [ "$COMMAND" != "status" ]; then
        warn "Test run failed (exit $exit_code) after ${elapsed}s."
        warn "If tests hung or ports conflict, run: ./scripts/test.sh reset"
    fi
    return "$exit_code"
}

trap on_exit EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

parse_global_flags() {
    while [ $# -gt 0 ]; do
        case "$1" in
            --build)
                DO_BUILD=true
                shift
                ;;
            --no-preflight)
                DO_PREFLIGHT=false
                warn "Skipping preflight cleanup — stale containers may cause hangs."
                shift
                ;;
            --keep-volumes)
                KEEP_VOLUMES=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            --)
                shift
                PYTEST_ARGS=("$@")
                return 0
                ;;
            *)
                return 0
                ;;
        esac
    done
    PYTEST_ARGS=()
}

compose_up_args() {
    local args=(up)
    if [ "$DO_BUILD" = true ]; then
        args+=(--build)
    fi
    echo "${args[@]}"
}

# pytest.ini addopts includes --pyargs igvfd.tests; passing another --pyargs on the
# CLI does not replace it — pytest collects the entire suite (~1300+ tests) and
# appears hung. Targeted runs must clear addopts and pass explicit plugin flags.
TARGETED_PYTEST_PREFIX=(
    pytest
    --override-ini
    addopts=
    -p
    igvfd.tests
    --instafail
    --assert=plain
)

build_targeted_pytest_cmd() {
    local -a default_args=("$@")
    local -a pytest_cmd=()

    if [ ${#PYTEST_ARGS[@]} -gt 0 ]; then
        if [ "${PYTEST_ARGS[0]}" = "pytest" ]; then
            if printf ' %s' "${PYTEST_ARGS[@]}" | grep -q ' --override-ini '; then
                pytest_cmd=("${PYTEST_ARGS[@]}")
            else
                pytest_cmd=("${TARGETED_PYTEST_PREFIX[@]}" "${PYTEST_ARGS[@]:1}")
            fi
        else
            pytest_cmd=("${TARGETED_PYTEST_PREFIX[@]}" "${PYTEST_ARGS[@]}")
        fi
    else
        pytest_cmd=("${TARGETED_PYTEST_PREFIX[@]}" "${default_args[@]}")
    fi

    PYTEST_CMD=("${pytest_cmd[@]}")
}

ensure_indexing_marker() {
    local arg
    for arg in "${PYTEST_CMD[@]}"; do
        if [[ "$arg" == -m* ]] && [[ "$arg" == *indexing* ]]; then
            return 0
        fi
    done
    local prefix_len="${#TARGETED_PYTEST_PREFIX[@]}"
    local -a with_marker=(
        "${PYTEST_CMD[@]:0:prefix_len}"
        -m indexing
        "${PYTEST_CMD[@]:prefix_len}"
    )
    PYTEST_CMD=("${with_marker[@]}")
}

wait_for_localstack() {
    local compose_file="$1"
    local timeout="${WAIT_FOR_SERVICES_TIMEOUT_SECONDS:-180}"
    log "Waiting for localstack (timeout ${timeout}s)..."
    local start=$SECONDS
    while true; do
        if docker compose -f "$compose_file" exec -T localstack \
            curl -sf http://localhost:4566/_localstack/init 2>/dev/null \
            | grep -q '"READY": true'; then
            log "Localstack is ready."
            return 0
        fi
        if [ $((SECONDS - start)) -ge "$timeout" ]; then
            warn "Timed out after ${timeout}s waiting for localstack."
            exit 1
        fi
        sleep 2
    done
}

run_unit_full() {
    COMPOSE_FILE="$COMPOSE_UNIT"
    local up_args
    up_args=($(compose_up_args))
    log "Running full unit suite: docker compose -f $COMPOSE_FILE ${up_args[*]} --exit-code-from pyramid"
    docker compose -f "$COMPOSE_FILE" "${up_args[@]}" --exit-code-from pyramid
}

run_unit_targeted() {
    COMPOSE_FILE="$COMPOSE_UNIT"
    local up_args
    up_args=($(compose_up_args))
    log "Starting unit fixtures: postgres, localstack"
    docker compose -f "$COMPOSE_FILE" "${up_args[@]}" -d postgres localstack
    wait_for_localstack "$COMPOSE_FILE"
    build_targeted_pytest_cmd -q --tb=short
    log "Running targeted unit tests"
    log "Command: docker compose -f $COMPOSE_FILE run --rm -e PYTHONUNBUFFERED=1 pyramid ${PYTEST_CMD[*]}"
    docker compose -f "$COMPOSE_FILE" run --rm -e PYTHONUNBUFFERED=1 pyramid "${PYTEST_CMD[@]}"
}

run_indexer_full() {
    COMPOSE_FILE="$COMPOSE_INDEXER"
    local up_args
    up_args=($(compose_up_args))
    log "Running full indexer suite: docker compose -f $COMPOSE_FILE ${up_args[*]} --exit-code-from indexer-tests"
    docker compose -f "$COMPOSE_FILE" "${up_args[@]}" --exit-code-from indexer-tests
}

run_indexer_targeted() {
    COMPOSE_FILE="$COMPOSE_INDEXER"
    local up_args
    up_args=($(compose_up_args))
    local services=(
        localstack postgres opensearch pyramid
        invalidation-service indexing-service deduplication-service
    )
    log "Starting indexer fixtures: ${services[*]}"
    docker compose -f "$COMPOSE_FILE" "${up_args[@]}" -d "${services[@]}"
    build_targeted_pytest_cmd -m indexing -q --tb=short
    ensure_indexing_marker
    log "Running targeted indexer tests"
    log "Command: docker compose -f $COMPOSE_FILE run --rm -e PYTHONUNBUFFERED=1 indexer-tests ${PYTEST_CMD[*]}"
    docker compose -f "$COMPOSE_FILE" run --rm -e PYTHONUNBUFFERED=1 indexer-tests "${PYTEST_CMD[@]}"
}

run_shell_unit() {
    COMPOSE_FILE="$COMPOSE_UNIT"
    local up_args
    up_args=($(compose_up_args))
    log "Starting unit fixtures for interactive shell"
    docker compose -f "$COMPOSE_FILE" "${up_args[@]}" -d postgres localstack
    wait_for_localstack "$COMPOSE_FILE"
    log "Opening interactive shell (exit bash to trigger teardown)"
    log "Tip: pytest --override-ini addopts= -p igvfd.tests --pyargs igvfd.tests.test_foo -q"
    docker compose -f "$COMPOSE_FILE" run --rm --service-ports pyramid /bin/bash
}

run_shell_indexer() {
    COMPOSE_FILE="$COMPOSE_INDEXER"
    local up_args
    up_args=($(compose_up_args))
    local services=(
        localstack postgres opensearch pyramid nginx
        invalidation-service indexing-service
    )
    log "Starting indexer fixtures for interactive shell"
    docker compose -f "$COMPOSE_FILE" "${up_args[@]}" -d "${services[@]}"
    log "Opening interactive shell (exit bash to trigger teardown)"
    docker compose -f "$COMPOSE_FILE" run --rm --service-ports indexer-tests /bin/bash
}

run_status() {
    TEARDOWN_DONE=true
    log "Containers matching igvfd:"
    docker ps -a --filter "name=igvfd" --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' || true
    echo
    if command -v lsof >/dev/null 2>&1; then
        log "Port usage (4566, 5432, 6543, 8000, 9200):"
        lsof -i :4566 -i :5432 -i :6543 -i :8000 -i :9200 2>/dev/null || echo "  (none)"
    fi
}

run_reset() {
    TEARDOWN_DONE=true
    COMPOSE_FILE=""
    preflight_cleanup
    check_ports
    log "Reset complete."
}

# --- main ---

if [ $# -lt 1 ]; then
    usage
    exit 1
fi

# Handle top-level --help before preflight.
if [ "$1" = "-h" ] || [ "$1" = "--help" ] || [ "$1" = "help" ]; then
    usage
    exit 0
fi

COMMAND="$1"
shift

PYTEST_ARGS=()
parse_global_flags "$@"

if [ "$DO_PREFLIGHT" = true ] && [ "$COMMAND" != "reset" ] && [ "$COMMAND" != "status" ]; then
    preflight_cleanup
    check_ports
fi

case "$COMMAND" in
    unit)
        if [ ${#PYTEST_ARGS[@]} -eq 0 ]; then
            run_unit_full
        else
            run_unit_targeted
        fi
        ;;
    indexer)
        if [ ${#PYTEST_ARGS[@]} -eq 0 ]; then
            run_indexer_full
        else
            run_indexer_targeted
        fi
        ;;
    shell)
        SUB="${1:-}"
        shift || true
        parse_global_flags "$@"
        case "$SUB" in
            unit) run_shell_unit ;;
            indexer) run_shell_indexer ;;
            *)
                echo "Usage: ./scripts/test.sh shell unit|indexer" >&2
                exit 1
                ;;
        esac
        ;;
    reset)
        run_reset
        ;;
    status)
        run_status
        ;;
    -h|--help|help)
        usage
        ;;
    *)
        echo "Unknown command: $COMMAND" >&2
        usage
        exit 1
        ;;
esac
