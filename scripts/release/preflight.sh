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

current_version=$(sed -n "s/^__version__ = '\(.*\)'$/\1/p" src/igvfd/__init__.py)
last_tag=$(git tag --sort=-v:refname | head -1)

echo "current __version__ : ${current_version}"
echo "latest tag          : ${last_tag}"
echo "origin/main         : $(git rev-parse --short origin/main)"
echo "origin/dev          : $(git rev-parse --short origin/dev)"
echo

if git merge-base --is-ancestor origin/main origin/dev; then
    echo "origin/main is an ancestor of origin/dev -- fast-forward merge is possible."
else
    echo "ERROR: origin/main is NOT an ancestor of origin/dev. The branches have diverged" >&2
    echo "       and 'git merge dev --ff-only' will fail. Resolve this before releasing." >&2
    exit 1
fi

echo
count=$(git rev-list --count origin/main..origin/dev)
echo "${count} commit(s) on origin/dev not yet on origin/main:"
echo
git log --pretty='  %h %s' origin/main..origin/dev
