#!/bin/bash
# Regression coverage for the release scripts.
#
# Makes no outward-facing change. Most checks -- phase detection, argument parsing, the
# token, the confirmation gate -- need neither network nor gh auth. The last group
# invokes the real scripts, which run 'git fetch -p --tags' and call gh; --offline skips
# those so CI can run the rest without repo credentials.
#
# Usage: scripts/release/test-release-scripts.sh [--offline]
set -uo pipefail

offline=0
[ "${1:-}" = "--offline" ] && offline=1

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

# Run under the SAME shell options as preflight.sh. Without -e a bare non-zero command
# only skips ahead, so this harness once passed while the real script aborted on it.
phase() {
    local want_rc="${4:-1}"
    (
        set -euo pipefail
        main_version="$1" dev_version="$2" last_tag="$3"
        released() { return "${want_rc}"; }
        # shellcheck disable=SC1090
        source "${phase_block}"
    ) 2>&1
}

check 'phase: bump on dev only' 'steps 4-6' \
    "$(phase 11.0.0 12.0.0 v11.0.0)"
# The regression this exists for: main and dev both at the new version reads as "no bump
# yet" unless the tag is consulted first.
check 'phase: pushed but untagged' 'step 9' \
    "$(phase 12.0.0 12.0.0 v11.0.0)"
check 'phase: tagged, no release' 'step 12' \
    "$(phase 12.0.0 12.0.0 v12.0.0 1)"
check 'phase: tagged and released' 'nothing in flight' \
    "$(phase 12.0.0 12.0.0 v12.0.0 0)"
check 'phase: gh unavailable' 'check by hand' \
    "$(phase 12.0.0 12.0.0 v12.0.0 2)"

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
# Only claim what it does: same action plus same sha gives the same token, a moved sha
# gives a different one. It is not a proof that --dry-run ran.
t1=$(release_token 'tag:12.0.0' 'deadbeef')
check 'token: stable for the same action' "${t1}" "$(release_token 'tag:12.0.0' 'deadbeef')"
if [ "${t1}" != "$(release_token 'tag:12.0.0' 'cafebabe')" ]; then
    pass=$((pass + 1)); echo 'ok   token: changes when the target moves'
else
    fail=$((fail + 1)); echo 'FAIL token: changes when the target moves'
fi

# --- require_confirmation, exercised directly -------------------------------------
conf() {
    bash -c 'source '"${here}"'/_common.sh
             dry_run=0; assume_yes='"$1"'; confirm_token='"$2"'
             require_confirmation v9.9.9 scope abcdef
             echo ACCEPTED' < /dev/null 2>&1
}
check 'confirm: non-tty without token refuses' 'not a tty' "$(conf 0 '')"
check 'confirm: --yes alone is not enough' 'not a tty' "$(conf 1 '')"
check 'confirm: wrong token rejected' 'does not match' "$(conf 0 nope)"
check 'confirm: right token accepted' 'ACCEPTED' \
    "$(conf 0 "$(release_token scope abcdef)")"
check 'confirm: dry run needs no confirmation' 'ACCEPTED' \
    "$(bash -c 'source '"${here}"'/_common.sh
                dry_run=1; assume_yes=0; confirm_token=
                require_confirmation v1 scope abcdef; echo ACCEPTED' < /dev/null 2>&1)"

# --- guards, via the real scripts (these need network and gh auth) ----------------
if [ "${offline}" = "1" ]; then
    echo 'skip guard checks (--offline: they fetch and call gh)'
    echo
    echo "${pass} passed, ${fail} failed"
    [ "${fail}" -eq 0 ]
    exit $?
fi

notes=$(mktemp); echo '- note' > "${notes}"
check 'guard: notes path must resolve' 'does not resolve' \
    "$(bash "${here}/tag.sh" 12.0.0 /nonexistent/dir/notes.md --dry-run 2>&1)"
check 'guard: publish needs a tag on origin' 'does not exist on origin' \
    "$(bash "${here}/publish-release.sh" 99.0.0 "${notes}" --dry-run 2>&1)"

# These reach past the uncommitted-changes guard, so they need a clean tree.
if [ -n "$(git status --porcelain --untracked-files=no 2>/dev/null)" ]; then
    echo 'skip guard: tag.sh version mismatch (tree has uncommitted changes)'
    echo 'skip guard: merge-to-main.sh version mismatch (tree has uncommitted changes)'
else
    check 'guard: tag.sh version mismatch' 'expected' \
        "$(bash "${here}/tag.sh" 99.0.0 "${notes}" --dry-run 2>&1)"
    # merge-to-main is the script that deploys staging, so its guards matter most. The
    # version guard deliberately precedes the local-branch guard, so this assertion holds
    # on a fresh clone that has only its default branch.
    check 'guard: merge-to-main.sh version mismatch' 'Merge the version bump PR' \
        "$(bash "${here}/merge-to-main.sh" 99.0.1 --dry-run 2>&1)"
fi
rm -f "${notes}"

echo
echo "${pass} passed, ${fail} failed"
[ "${fail}" -eq 0 ]
