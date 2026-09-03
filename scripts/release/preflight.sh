#!/bin/bash
# Read-only survey of the release state, including which runbook step comes next.
# Changes nothing, so it is always safe to run.
# Usage: scripts/release/preflight.sh
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: working tree is dirty. Commit or stash before releasing." >&2
    git status --short >&2
    exit 1
fi

git fetch origin -p --tags

read_version() {
    local v
    v=$(git show "$1:src/igvfd/__init__.py" | sed -n "s/^__version__ = '\(.*\)'\$/\1/p")
    # sed -n exits 0 on no match, so an unparsed version would otherwise sail through as
    # an empty string and compare equal to the other empty string.
    if [ -z "${v}" ]; then
        echo "ERROR: could not parse __version__ from $1:src/igvfd/__init__.py" >&2
        exit 1
    fi
    printf '%s' "${v}"
}

# Read from the remote refs, not the working tree: mid-release the operator is often
# sitting on the bump branch, where the working tree would report the new version as
# though it were already released.
main_version=$(read_version origin/main)
dev_version=$(read_version origin/dev)
# Not piped into head, which can take SIGPIPE and trip pipefail.
last_tag=$(git tag --list 'v*' --sort=-v:refname)
last_tag=${last_tag%%$'\n'*}

echo "origin/main : $(git rev-parse --short origin/main)  __version__ = ${main_version}"
echo "origin/dev  : $(git rev-parse --short origin/dev)  __version__ = ${dev_version}"
echo "latest tag  : ${last_tag:-<none>}"
echo

if ! git merge-base --is-ancestor origin/main origin/dev; then
    echo "ERROR: origin/main is NOT an ancestor of origin/dev. The branches have diverged" >&2
    echo "       and 'git merge dev --ff-only' will fail. A merge commit on main (rather" >&2
    echo "       than a fast-forward) is the usual cause; merging main back into dev" >&2
    echo "       restores the invariant." >&2
    exit 1
fi

# Phase detection. The tag has to be consulted before the version comparison: right after
# step 6 main and dev are both at the NEW version, which is indistinguishable from "no
# bump yet" on versions alone, and misreading it would send the operator off to bump again
# for a release that is already live on staging.
if [ "${main_version}" != "${dev_version}" ]; then
    echo "NEXT: a bump to ${dev_version} is on dev but not on main -> steps 4-6 (PR to main, then merge-to-main.sh)."
elif [ "${last_tag}" != "v${main_version}" ]; then
    echo "NEXT: main is at ${main_version} and untagged -> step 9 (tag.sh)."
    echo "      If you have not pushed main yet, this is instead steps 2-3 (pick a version, bump PR)."
elif gh release view "${last_tag}" --repo "$(gh repo view --json nameWithOwner --jq .nameWithOwner)" >/dev/null 2>&1; then
    echo "NEXT: ${last_tag} is tagged and released -> nothing in flight; steps 2-3 for the next release."
else
    echo "NEXT: ${last_tag} is tagged but has no GitHub Release -> step 12 (publish-release.sh)."
fi
echo

count=$(git rev-list --count origin/main..origin/dev)
echo "${count} commit(s) on origin/dev not yet on origin/main:"
echo
git log --pretty='  %h %s' origin/main..origin/dev
