#!/bin/bash
# Each wait gives up after WAIT_FOR_SERVICES_TIMEOUT seconds (default 300) rather than
# looping forever: an OpenSearch that never came up used to hang CI for over an hour
# with nothing in the log. curl's --max-time keeps one stalled request from blocking
# the loop past the deadline.
TIMEOUT=${WAIT_FOR_SERVICES_TIMEOUT:-300}

wait_for() {
    local name=$1 url=$2 pattern=$3
    local deadline=$((SECONDS + TIMEOUT))
    local response
    until response=$(curl -sS --max-time 5 "$url" 2>&1) && grep -q "$pattern" <<< "$response"; do
        if (( SECONDS >= deadline )); then
            echo "Timed out after ${TIMEOUT}s waiting for $name at $url. Last response:" >&2
            head -c 1000 <<< "$response" >&2
            exit 1
        fi
        echo "Waiting for $name to become ready..."
        sleep 5
    done
    echo "$name is ready."
}

wait_for Localstack http://localstack:4566/_localstack/init '"READY": true'
wait_for Opensearch http://opensearch:9200 '"cluster_name"'

exec "$@"
