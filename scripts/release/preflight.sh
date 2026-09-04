#!/bin/bash
# Survey of the release state, including which runbook step comes next.
#
# Makes no outward-facing change and never touches the working tree. It does run
# 'git fetch -p --tags', which updates and prunes local remote-tracking refs, and it
# needs gh only to report whether a GitHub Release exists.
# Usage: scripts/release/preflight.sh
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

cd "$(git rev-parse --show-toplevel)"

# Untracked files are deliberately tolerated: they cannot affect a checkout, an ff-only
# merge or a tag, and refusing on them means any stray scratch file blocks a release.
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    echo "ERROR: working tree has uncommitted changes. Commit or stash before releasing." >&2
    git status --short --untracked-files=no >&2
    exit 1
fi

git fetch origin -p --tags

main_version=$(read_version_from origin/main)
dev_version=$(read_version_from origin/dev)
# Reachable from main rather than the highest v* in the repo, so a tag pushed from some
# other branch cannot skew the phase detection below.
last_tag=$(git describe --tags --abbrev=0 --match 'v*' origin/main 2>/dev/null || true)

echo "origin/main : $(git rev-parse --short origin/main)  __version__ = ${main_version}"
echo "origin/dev  : $(git rev-parse --short origin/dev)  __version__ = ${dev_version}"
echo "latest tag  : ${last_tag:-<none>}"
echo

if ! git merge-base --is-ancestor origin/main origin/dev; then
    echo "ERROR: origin/main is NOT an ancestor of origin/dev. The branches have diverged" >&2
    echo "       and 'git merge dev --ff-only' will fail. Anything that rewrites or adds" >&2
    echo "       commits on main -- a merge commit, or GitHub's rebase-and-merge -- causes" >&2
    echo "       this. Merging main back into dev restores the invariant." >&2
    exit 1
fi

# Resolved up front rather than inside the conditional below, so a gh failure surfaces as
# itself instead of being read as "no Release exists".
repo=""
gh_ok=0
if repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null); then
    gh_ok=1
fi

released() {
    [ "${gh_ok}" = "1" ] || return 2
    gh release view "$1" --repo "${repo}" >/dev/null 2>&1
}

# Phase detection. The tag has to be consulted before the version comparison: right after
# step 6 main and dev are both at the NEW version, which is indistinguishable from "no
# bump yet" on versions alone, and misreading it would send the operator off to bump again
# for a release that is already live on staging.
if [ "${main_version}" != "${dev_version}" ]; then
    echo "NEXT: a bump to ${dev_version} is on dev but not on main -> steps 4-6 (PR to main, then merge-to-main.sh)."
elif [ "${last_tag}" != "v${main_version}" ]; then
    echo "NEXT: main is at ${main_version} and untagged -> step 9 (tag.sh)."
    echo "      If you have not pushed main yet, this is instead steps 2-3 (pick a version, bump PR)."
else
    # Captured rather than called bare: under set -e a non-zero return would exit here
    # and the case below would never run.
    rc=0
    released "${last_tag}" || rc=$?
    case ${rc} in
        0) echo "NEXT: ${last_tag} is tagged and released -> nothing in flight; steps 2-3 for the next release." ;;
        1) echo "NEXT: ${last_tag} is tagged but has no GitHub Release -> step 12 (publish-release.sh)." ;;
        *) echo "NEXT: ${last_tag} is tagged. Could not reach gh to check for a GitHub Release --"
           echo "      check by hand whether step 12 is still outstanding." ;;
    esac
fi
echo

count=$(git rev-list --count origin/main..origin/dev)
if [ "${count}" = "0" ]; then
    echo "origin/main is level with origin/dev; nothing pending."
else
    echo "${count} commit(s) on origin/dev not yet on origin/main:"
    echo
    git log --pretty='  %h %s' origin/main..origin/dev
fi
