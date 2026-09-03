#!/bin/bash
# Step 6 of docs/staging_deploy.md: fast-forward main to dev and push, which deploys
# staging. Refuses to proceed unless everything is exactly as expected.
#
# Pushing main deploys staging unconditionally -- the AWS manual approval later in the
# runbook gates the production/sandbox promotion, not this. So this script confirms
# before pushing unless --yes is passed.
#
# Usage: scripts/release/merge-to-main.sh X.Y.Z [--yes]
set -euo pipefail

version="${1:?usage: merge-to-main.sh X.Y.Z [--yes]}"
assume_yes="${2:-}"

cd "$(git rev-parse --show-toplevel)"
start_branch=$(git rev-parse --abbrev-ref HEAD)

# Any failure past this point returns the operator to where they started, so a failed
# run never silently strands them on main or dev.
restore_branch() { git checkout -q "${start_branch}" 2>/dev/null || true; }
trap restore_branch EXIT

if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: working tree is dirty. Commit or stash first." >&2
    exit 1
fi

git fetch origin -p --tags

# Not because this script tags -- it does not -- but because an existing tag means this
# version was already released, and the operator has almost certainly mistyped.
if git rev-parse -q --verify "refs/tags/v${version}" >/dev/null; then
    echo "ERROR: tag v${version} already exists, so ${version} looks already released." >&2
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

target=$(git rev-parse --short origin/dev)
count=$(git rev-list --count origin/main..origin/dev)

echo
echo "About to fast-forward main to ${target} (${count} commit(s)) and push."
echo "This DEPLOYS STAGING immediately. It does not touch production."
echo
if [ "${assume_yes}" != "--yes" ]; then
    if [ ! -t 0 ]; then
        echo "ERROR: not a tty and --yes not given; refusing to deploy unconfirmed." >&2
        exit 1
    fi
    read -r -p "Type the version to confirm (${version}): " reply
    if [ "${reply}" != "${version}" ]; then
        echo "Aborted; nothing pushed." >&2
        exit 1
    fi
fi

git checkout dev
git merge origin/dev --ff-only
git checkout main
git merge origin/main --ff-only

# --ff-only is the safety gate from the doc: it fails rather than creating a merge commit.
if ! git merge dev --ff-only; then
    echo "ERROR: fast-forward merge failed. Do NOT push. Resolve manually." >&2
    exit 1
fi

echo
echo "main is now at $(git rev-parse --short HEAD) ($(git log -1 --pretty=%s))"

if ! git push origin main; then
    echo >&2
    echo "ERROR: push to main was rejected, most likely by branch protection." >&2
    echo "       Local main was fast-forwarded but NOT pushed; nothing is deployed." >&2
    echo >&2
    echo "       If you fall back to merging the dev -> main PR on GitHub, use a method" >&2
    echo "       that keeps main a fast-forward of dev -- 'gh pr merge <PR> --rebase'." >&2
    echo "       A merge commit ('--merge') makes main stop being an ancestor of dev, and" >&2
    echo "       preflight.sh will then fail on every later release until main is merged" >&2
    echo "       back into dev." >&2
    exit 1
fi

echo
echo "Pushed. Staging is deploying. Monitor #aws-igvf-staging for batch-upgrade errors (step 10)."
