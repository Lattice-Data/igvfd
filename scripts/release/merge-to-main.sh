#!/bin/bash
# Step 6 of docs/staging_deploy.md: fast-forward main to dev and push, which deploys
# staging. Refuses to proceed unless everything is exactly as expected.
#
# Pushing main deploys staging unconditionally -- the AWS manual approval later in the
# runbook gates the production/sandbox promotion, not this.
#
# Usage: scripts/release/merge-to-main.sh X.Y.Z [--dry-run] [--yes|--confirm-token=X]
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
parse_release_args "$@"
version="${POSITIONAL[0]:?usage: merge-to-main.sh X.Y.Z [--dry-run] [--yes|--confirm-token=X]}"
expect_positional_count 1

cd "$(git rev-parse --show-toplevel)"
start_ref=$(current_ref)

# Any failure past this point returns the operator to where they started, so a failed
# run never silently strands them on main or dev.
restore_ref() { git checkout -q "${start_ref}" 2>/dev/null || true; }
trap restore_ref EXIT

# Untracked files are tolerated: the release notes live in the worktree between steps 9
# and 12, and an untracked file cannot affect a checkout or an ff-only merge.
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    echo "ERROR: working tree has uncommitted changes. Commit or stash first." >&2
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

repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
target=$(git rev-parse --short origin/dev)
count=$(git rev-list --count origin/main..origin/dev)

if [ "${count}" = "0" ]; then
    echo "Nothing to do: origin/main is already at origin/dev (${target})."
    exit 0
fi

echo
echo "About to fast-forward main to ${target} (${count} commit(s)) and push."
echo "This DEPLOYS STAGING immediately. It does not touch production."
echo
require_confirmation "${version}" "merge-to-main:${version}" "$(git rev-parse origin/dev)"

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
    echo "       Do NOT fall back to 'gh pr merge'. Both --merge and --rebase stop main" >&2
    echo "       from being a fast-forward of dev: --merge adds a merge commit, --rebase" >&2
    echo "       rewrites the commits with new shas. Either way preflight.sh fails on" >&2
    echo "       every later release until main is merged back into dev." >&2
    echo >&2
    echo "       To move main while preserving the shas, update the ref directly:" >&2
    echo "         gh api -X PATCH repos/${repo}/git/refs/heads/main \\" >&2
    echo "           -f sha=$(git rev-parse origin/dev)" >&2
    exit 1
fi

if [ "${dry_run}" = "1" ]; then
    print_dry_run_footer "merge-to-main:${version}" "$(git rev-parse origin/dev)" \
        "scripts/release/merge-to-main.sh ${version}"
    exit 0
fi
echo
echo "Pushed. Staging is deploying. Monitor #aws-igvf-staging for batch-upgrade errors (step 10)."
