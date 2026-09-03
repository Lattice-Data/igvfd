#!/bin/bash
# Step 6 of docs/staging_deploy.md: fast-forward main to dev and push, which deploys
# staging. Refuses to proceed unless everything is exactly as expected.
#
# Pushing main deploys staging unconditionally -- the AWS manual approval later in the
# runbook gates the production/sandbox promotion, not this.
#
# Usage: scripts/release/merge-to-main.sh X.Y.Z [--yes] [--dry-run]
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
parse_release_args "$@"
version="${POSITIONAL[0]:?usage: merge-to-main.sh X.Y.Z [--yes] [--dry-run]}"

cd "$(git rev-parse --show-toplevel)"
start_ref=$(current_ref)

# Any failure past this point returns the operator to where they started, so a failed
# run never silently strands them on main or dev.
restore_ref() { git checkout -q "${start_ref}" 2>/dev/null || true; }
trap restore_ref EXIT

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
dev_version=$(read_version_from origin/dev)
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
require_confirmation "${version}"

# Advancing local dev and main to match their remotes mirrors the runbook's step 6
# verbatim. More working-tree churn than the fast-forward strictly needs, but it keeps
# the local branches in the state the rest of the runbook assumes.
run git checkout dev
run git merge origin/dev --ff-only
run git checkout main
run git merge origin/main --ff-only

# --ff-only is the safety gate from the doc: it fails rather than creating a merge commit.
if ! run git merge dev --ff-only; then
    echo "ERROR: fast-forward merge failed. Do NOT push. Resolve manually." >&2
    exit 1
fi

if [ "${dry_run}" != "1" ]; then
    echo
    echo "main is now at $(git rev-parse --short HEAD) ($(git log -1 --pretty=%s))"
fi

if ! run git push origin main; then
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
if [ "${dry_run}" = "1" ]; then
    echo "Dry run complete. Every guard passed; nothing was merged or pushed."
    exit 0
fi
echo "Pushed. Staging is deploying. Monitor #aws-igvf-staging for batch-upgrade errors (step 10)."
