#!/bin/bash
# Read-only survey of the release state. Changes nothing, so it is always safe to run.
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
    git show "$1:src/igvfd/__init__.py" | sed -n "s/^__version__ = '\(.*\)'$/\1/p"
}

# Read from the remote refs, not the working tree: mid-release the operator is often
# sitting on the bump branch, where the working tree would report the new version as
# though it were already released. The main/dev pair is what identifies the phase.
main_version=$(read_version origin/main)
dev_version=$(read_version origin/dev)
last_tag=$(git tag --list 'v*' --sort=-v:refname | head -1)

echo "origin/main : $(git rev-parse --short origin/main)  __version__ = ${main_version}"
echo "origin/dev  : $(git rev-parse --short origin/dev)  __version__ = ${dev_version}"
echo "latest tag  : ${last_tag:-<none>}"
echo

if [ "${main_version}" != "${dev_version}" ]; then
    echo "A version bump to ${dev_version} is already on dev but not yet on main."
else
    echo "No version bump on dev yet -- main and dev are both at ${main_version}."
fi
echo

if git merge-base --is-ancestor origin/main origin/dev; then
    echo "origin/main is an ancestor of origin/dev -- fast-forward merge is possible."
else
    echo "ERROR: origin/main is NOT an ancestor of origin/dev. The branches have diverged" >&2
    echo "       and 'git merge dev --ff-only' will fail. A merge commit on main (rather" >&2
    echo "       than a fast-forward) is the usual cause; merging main back into dev" >&2
    echo "       restores the invariant." >&2
    exit 1
fi

echo
count=$(git rev-list --count origin/main..origin/dev)
echo "${count} commit(s) on origin/dev not yet on origin/main:"
echo
git log --pretty='  %h %s' origin/main..origin/dev
