#!/bin/bash
# Cheap regression coverage for the release scripts. Runs no side effects: it exercises
# the phase-detection logic with injected state and the guards via --dry-run.
#
# Usage: scripts/release/test-release-scripts.sh
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${here}/_common.sh"

pass=0
fail=0

check() {
    local name="$1" expected="$2" actual="$3"
    if [[ "${actual}" == *"${expected}"* ]]; then
        pass=$((pass + 1))
        printf 'ok   %s\n' "${name}"
    else
        fail=$((fail + 1))
        printf 'FAIL %s\n       want substring: %s\n       got: %s\n' "${name}" "${expected}" "${actual}"
    fi
}

# --- phase detection -------------------------------------------------------------
# Extracted rather than reimplemented, so the test breaks if the real logic changes.
phase_block=$(mktemp)
sed -n '/^# Phase detection/,/^fi$/p' "${here}/preflight.sh" > "${phase_block}"
trap 'rm -f "${phase_block}"' EXIT

phase() {
    main_version="$1" dev_version="$2" last_tag="$3"
    released() { return "${4:-1}"; }
    source "${phase_block}" | head -1
}

check 'phase: bump on dev only' 'steps 4-6' \
    "$(phase 11.0.0 12.0.0 v11.0.0)"
# The regression this test exists for: main and dev both at the new version reads as
# "no bump yet" unless the tag is consulted first.
check 'phase: pushed but untagged' 'step 9' \
    "$(phase 12.0.0 12.0.0 v11.0.0)"
check 'phase: tagged, no release' 'step 12' \
    "$(phase 12.0.0 12.0.0 v12.0.0)"
check 'phase: tagged and released' 'nothing in flight' \
    "$(released() { return 0; }; main_version=12.0.0 dev_version=12.0.0 last_tag=v12.0.0; source "${phase_block}" | head -1)"
check 'phase: gh unavailable' 'check by hand' \
    "$(released() { return 2; }; main_version=12.0.0 dev_version=12.0.0 last_tag=v12.0.0; source "${phase_block}" | head -2 | tail -1)"

# --- argument parsing ------------------------------------------------------------
check 'args: flag before positional' '12.0.0' \
    "$(parse_release_args --yes 12.0.0; echo "${POSITIONAL[0]}")"
check 'args: token parsed' 'abc12345' \
    "$(parse_release_args 12.0.0 --confirm-token=abc12345; echo "${confirm_token}")"
check 'args: unknown flag rejected' 'unknown flag' \
    "$(bash -c 'source '"${here}"'/_common.sh; parse_release_args --bogus' 2>&1)"
check 'args: extra positional rejected' 'unexpected extra argument' \
    "$(bash -c 'source '"${here}"'/_common.sh; parse_release_args a b c; expect_positional_count 2' 2>&1)"

# --- token ------------------------------------------------------------------------
t1=$(release_token 'tag:12.0.0' 'deadbeef')
t2=$(release_token 'tag:12.0.0' 'deadbeef')
t3=$(release_token 'tag:12.0.0' 'cafebabe')
check 'token: stable for same action' "${t1}" "${t2}"
[ "${t1}" != "${t3}" ] && { pass=$((pass + 1)); echo 'ok   token: changes when target moves'; } \
    || { fail=$((fail + 1)); echo 'FAIL token: changes when target moves'; }

# --- guards, via real invocations that must not have side effects -----------------
check 'guard: notes file must exist' 'does not resolve' \
    "$(bash "${here}/tag.sh" 12.0.0 /nonexistent/dir/notes.md --dry-run 2>&1)"

notes=$(mktemp); echo '- note' > "${notes}"
check 'guard: publish needs a tag on origin' 'does not exist on origin' \
    "$(bash "${here}/publish-release.sh" 99.0.0 "${notes}" --dry-run 2>&1)"

# These reach past the uncommitted-changes guard, so they need a clean tree.
if [ -n "$(git -C "${here}" status --porcelain --untracked-files=no)" ]; then
    echo 'skip guard: version must match origin/main (tree has uncommitted changes)'
    echo 'skip guard: non-tty refuses without token (tree has uncommitted changes)'
else
    check 'guard: version must match origin/main' 'expected' \
        "$(bash "${here}/tag.sh" 99.0.0 "${notes}" --dry-run 2>&1)"
    # Uses the latest real tag, so it gets past the tag check and reaches confirmation.
    latest=$(git -C "${here}" tag --list 'v*' --sort=-v:refname); latest=${latest%%$'\n'*}
    check 'guard: non-tty refuses without token' 'not a tty' \
        "$(bash "${here}/publish-release.sh" "${latest#v}" "${notes}" < /dev/null 2>&1)"
fi
check 'guard: wrong token rejected' 'does not match' \
    "$(bash -c 'source '"${here}"'/_common.sh; dry_run=0; assume_yes=0; confirm_token=nope; require_confirmation v1 scope sha' 2>&1)"
rm -f "${notes}"

echo
echo "${pass} passed, ${fail} failed"
[ "${fail}" -eq 0 ]
