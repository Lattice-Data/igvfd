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

# --- version parsing and path resolution ------------------------------------------
# Both are offline and local, and read_version_from's sed pattern is the single point of
# failure for the version guards in merge-to-main.sh and tag.sh -- so they belong in the
# group CI can run.
# Run under the real scripts' shell options. Under a plain bash -c these guards appear to
# work while the real caller aborts earlier on a pipefail -- the same way the phase
# harness once passed against a broken preflight.
strict() {
    bash -c "set -euo pipefail; source '${here}/_common.sh'; $1" 2>&1
}

check 'version: parses from a local ref' 'MATCHED' \
    "$(strict 'v=$(read_version_from HEAD); [[ "${v}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] && echo MATCHED || echo "got ${v}"')"
check 'version: errors when the file is absent' 'cannot read' \
    "$(strict 'read_version_from deadbeefnotaref')"
# The reachable half of the guard: git show succeeds but the pattern does not match.
# Built from loose objects so no ref is touched.
synthetic_tree() {
    local blob inner mid
    blob=$(printf "__VERSION__ = '1.0.0'\n" | git hash-object -w --stdin)
    inner=$(printf '100644 blob %s\t__init__.py\n' "${blob}" | git mktree)
    mid=$(printf '040000 tree %s\tigvfd\n' "${inner}" | git mktree)
    printf '040000 tree %s\tsrc\n' "${mid}" | git mktree
}
check 'version: errors when the pattern does not match' 'could not parse __version__' \
    "$(strict "read_version_from $(synthetic_tree)")"
check 'path: resolves a relative path' "${here}/_common.sh" \
    "$(cd "${here}" && resolve_path ./_common.sh)"
check 'path: fails on a missing directory' 'FAILED' \
    "$(resolve_path /nonexistent/dir/notes.md || echo FAILED)"

# --- run(), the basis of the entire --dry-run story -------------------------------
marker=$(mktemp -u)
check 'dry run: run() does not execute the command' 'NOT EXECUTED' \
    "$(dry_run=1; run touch "${marker}" >/dev/null; [ -e "${marker}" ] && echo EXECUTED || echo NOT EXECUTED)"
check 'dry run: run() prints what it would do' 'DRY RUN: touch' \
    "$(dry_run=1; run touch "${marker}")"
check 'dry run: run() does execute when not dry' 'EXECUTED' \
    "$(dry_run=0; run touch "${marker}" >/dev/null; [ -e "${marker}" ] && echo EXECUTED || echo 'NOT EXECUTED')"
rm -f "${marker}"

# --- release notes survive the annotated tag --------------------------------------
# In a throwaway repo, so this is offline and touches nothing here. git tag defaults to
# --cleanup=strip, which eats every markdown heading; the resume path in SKILL.md reads
# the notes back out of the tag, so a lossy round-trip would hand back wrong notes while
# calling them the originals.
notes_repo=$(mktemp -d)
# An explicit identity: CI runners have no global user.name/user.email and git's
# hostname-based fallback fails there, so both the commit and the annotated tag would
# refuse. Output is captured rather than discarded -- swallowing it is why the first CI
# failure of this block reported only "lost:" with no cause.
notes_setup=$( (
    cd "${notes_repo}" || exit 1
    export GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=test@example.com \
           GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=test@example.com
    git init -q . || exit 1
    git commit -q --allow-empty -m init || exit 1
    printf '## DB2-1: a change\n- detail\n\n## Other\n- housekeeping\n' > n.md
    # v1 mirrors the flags tag.sh uses; v2 pins git's default for comparison.
    git tag -a v1 --cleanup=whitespace -F n.md || exit 1
    git tag -l --format='%(contents)' v1 > out.md || exit 1
    git tag -a v2 -F n.md || exit 1
    git tag -l --format='%(contents)' v2 > default.md || exit 1
# The redirect belongs inside the substitution: outside it applies to the assignment and
# stderr escapes to the terminal instead of being captured.
) 2>&1 )
notes_setup_rc=$?

if [ "${notes_setup_rc}" != "0" ]; then
    fail=$((fail + 2))
    printf 'FAIL notes: could not set up the throwaway repo (rc=%s)\n       %s\n' \
        "${notes_setup_rc}" "${notes_setup}"
    printf 'FAIL notes: skipped, setup failed\n'
else
    check 'notes: headings survive the tag round-trip' 'HEADINGS KEPT' \
        "$(if grep -q '^## Other' "${notes_repo}/out.md" \
              && grep -q '^## DB2-1: a change' "${notes_repo}/out.md"; then
               echo 'HEADINGS KEPT'
           else
               echo "lost: $(cat "${notes_repo}/out.md")"
           fi)"
    # Asserts the file exists first: without that this passes vacuously when setup fails,
    # because grep on a missing file also reports "no headings found". That is exactly how
    # it passed in the CI run where the round-trip check failed.
    check 'notes: default cleanup would lose them (documents why the flag is needed)' 'STRIPPED' \
        "$(if [ ! -f "${notes_repo}/default.md" ]; then
               echo 'MISSING default.md'
           elif grep -q '^## ' "${notes_repo}/default.md"; then
               echo 'KEPT -- git changed, revisit tag.sh'
           else
               echo STRIPPED
           fi)"
fi
rm -rf "${notes_repo}"

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
    # The overwrite pre-check must agree with what git actually refuses on. In a clean
    # checkout there is no overlap; the intersection is what merge-to-main.sh computes.
    check 'guard: no untracked files would be overwritten' 'NO CLASH' \
        "$(c=$(comm -12 <(git ls-files --others --exclude-standard | sort) \
                        <(git ls-tree -r --name-only origin/dev | sort)); \
           [ -z "${c}" ] && echo 'NO CLASH' || echo "would clash: ${c}")"
fi
rm -f "${notes}"

echo
echo "${pass} passed, ${fail} failed"
[ "${fail}" -eq 0 ]
