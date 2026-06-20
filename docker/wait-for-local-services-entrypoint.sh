#!/bin/bash
set -euo pipefail

TIMEOUT="${WAIT_FOR_SERVICES_TIMEOUT_SECONDS:-180}"

wait_for_service() {
    local name="$1"
    local url="$2"
    local grep_pattern="$3"
    local start=$SECONDS
    local last_output=""

    while true; do
        last_output="$(curl -s "$url" 2>&1 || true)"
        if echo "$last_output" | grep -q "$grep_pattern"; then
            echo "$name is ready."
            return 0
        fi
        if [ $((SECONDS - start)) -ge "$TIMEOUT" ]; then
            echo "ERROR: Timed out after ${TIMEOUT}s waiting for $name (url: $url)" >&2
            echo "Last response:" >&2
            echo "$last_output" >&2
            exit 1
        fi
        echo "Waiting for $name to become ready..."
        sleep 5
    done
}

wait_for_service "Localstack" "http://localstack:4566/_localstack/init" '"READY": true'
wait_for_service "Opensearch" "http://opensearch:9200" '"cluster_name"'

exec "$@"
