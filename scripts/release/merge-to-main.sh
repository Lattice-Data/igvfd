#!/bin/bash
# Step 6 of docs/staging_deploy.md: fast-forward main to dev and push, which triggers
# the staging deployment. Refuses to proceed unless everything is exactly as expected.
# Usage: scripts/release/merge-to-main.sh X.Y.Z
set -euo pipefail

version="${1:?usage: merge-to-main.sh X.Y.Z}"

cd "$(git rev-parse --show-toplevel)"
start_branch=$(git rev-parse --abbrev-ref HEAD)

if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: working tree is dirty. Commit or stash first." >&2
    exit 1
fi

git fetch origin -p --tags

if git rev-parse -q --verify "refs/tags/v${version}" >/dev/null; then
    echo "ERROR: tag v${version} already exists. Pick a new version." >&2
    exit 1
fi

if ! git merge-base --is-ancestor origin/main origin/dev; then
    echo "ERROR: origin/main is not an ancestor of origin/dev; fast-forward is impossible." >&2
    exit 1
fi

# The version bump (step 3) must already be merged to dev, or staging deploys the wrong number.
dev_version=$(git show origin/dev:src/igvfd/__init__.py | sed -n "s/^__version__ = '\(.*\)'$/\1/p")
if [ "${dev_version}" != "${version}" ]; then
    echo "ERROR: origin/dev has __version__ = '${dev_version}', expected '${version}'." >&2
    echo "       Merge the version bump PR to dev first (step 3)." >&2
    exit 1
fi

git checkout dev
git merge origin/dev --ff-only
git checkout main
git merge origin/main --ff-only

# --ff-only is the safety gate from the doc: it fails rather than creating a merge commit.
if ! git merge dev --ff-only; then
    echo "ERROR: fast-forward merge failed. Do NOT push. Resolve manually." >&2
    git checkout "${start_branch}"
    exit 1
fi

echo
echo "main is now at $(git rev-parse --short HEAD) ($(git log -1 --pretty=%s))"
echo "Pushing to origin/main -- this triggers the staging deployment."

if ! git push origin main; then
    echo >&2
    echo "ERROR: push to main was rejected, most likely by branch protection." >&2
    echo "       Fall back to merging the dev -> main PR on GitHub:" >&2
    echo "         gh pr merge --repo Lattice-Data/igvfd <PR> --merge" >&2
    echo "       Local main has been fast-forwarded but NOT pushed; nothing is deployed." >&2
    exit 1
fi

echo
echo "Pushed. Staging is deploying. Monitor #aws-igvf-staging for batch-upgrade errors (step 9)."
