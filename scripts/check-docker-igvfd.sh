#!/usr/bin/env bash
# Warn if igvfd Docker containers exist (does not block commits).
set -euo pipefail

count=0
for filter in igvfd igvfd-dev igvfd-test igvfd-test-indexer; do
    n="$(docker ps -aq --filter "name=${filter}" 2>/dev/null | wc -l | tr -d ' ')"
    count=$((count + n))
done

if [ "$count" -gt 0 ]; then
    echo "WARNING: ${count} igvfd Docker container(s) found." >&2
    echo "Stale containers can cause test hangs. Run: ./scripts/test.sh reset" >&2
fi

exit 0
