#!/bin/bash
# Step 6 of docs/staging_deploy.md: fast-forward main to dev and push, which deploys
# staging. Refuses to proceed unless everything is exactly as expected.
#
# Pushing main deploys staging unconditionally -- the AWS manual approval later in the
# runbook gates the production/sandbox promotion, not this.
#
# Usage: scripts/release/merge-to-main.sh X.Y.Z [--dry-run] [--yes|--confirm-token=X]
set -euo pipefail

# shellcheck source-path=SCRIPTDIR
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

# Untracked files do not block a release by themselves, so they are not grounds to
# refuse -- but they are not harmless either: see the overwrite pre-check below.
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    echo "ERROR: working tree has uncommitted changes. Commit or stash first." >&2
    exit 1
fi

git fetch origin -p --tags

# Not because this script tags -- it does not -- but because an existing tag means this
# version was already released, and the operator has almost certainly mistyped. Asked of
# the remote: 'fetch -p' prunes branches but not tags, so a tag deleted upstream lingers
# locally and a local-only check would block the release on stale state.
if git ls-remote --exit-code --tags origin "refs/tags/v${version}" >/dev/null 2>&1; then
    echo "ERROR: tag v${version} exists on origin, so ${version} looks already released." >&2
    exit 1
fi

if ! git merge-base --is-ancestor origin/main origin/dev; then
    echo "ERROR: origin/main is not an ancestor of origin/dev; fast-forward is impossible." >&2
    exit 1
fi

# The version bump (step 3) must already be merged to dev, or staging deploys the wrong
# number. Checked before anything about local branches: it reads only origin/dev, and a
# wrong version is the more useful thing to hear about first.
dev_version=$(read_version_from origin/dev)
if [ "${dev_version}" != "${version}" ]; then
    echo "ERROR: origin/dev has __version__ = '${dev_version}', expected '${version}'." >&2
    echo "       Merge the version bump PR to dev first (step 3)." >&2
    exit 1
fi

# Step 6 checks both branches out and fast-forwards each to its remote. Assert both are
# possible now rather than discovering it at the merge: those merges run only for real,
# so without this a dry run would report success and the real run would then die on git's
# bare "Not possible to fast-forward" right after the operator confirmed.
for branch in dev main; do
    if ! git rev-parse -q --verify "refs/heads/${branch}" >/dev/null; then
        echo "ERROR: no local '${branch}' branch. Create it first:" >&2
        echo "         git branch ${branch} origin/${branch}" >&2
        exit 1
    fi
    if ! git merge-base --is-ancestor "refs/heads/${branch}" "origin/${branch}"; then
        echo "ERROR: local '${branch}' has commits not on origin/${branch}, so it cannot be" >&2
        echo "       fast-forwarded. Reconcile it first, e.g.:" >&2
        echo "         git checkout ${branch} && git status" >&2
        exit 1
    fi
    # git checkout and git merge --ff-only both abort with "would be overwritten" when the
    # incoming tree tracks a path that exists here untracked. Those commands run only for
    # real, so without this the dry run would report success and the real run would die on
    # the checkout right after the operator confirmed.
    clash=$(comm -12 \
        <(git ls-files --others --exclude-standard | sort) \
        <(git ls-tree -r --name-only "origin/${branch}" | sort))
    if [ -n "${clash}" ]; then
        echo "ERROR: these untracked files would be overwritten by checking out ${branch}:" >&2
        printf '%s\n' "${clash}" | sed 's/^/         /' >&2
        echo "       Move or remove them first." >&2
        exit 1
    fi
done

target=$(git rev-parse --short origin/dev)
count=$(git rev-list --count origin/main..origin/dev)
# Spelled once: the confirmation and the footer must agree on scope and sha, or the token
# the dry run prints is never accepted.
scope="merge-to-main:${version}"
target_sha=$(git rev-parse origin/dev)

if [ "${count}" = "0" ]; then
    echo "Nothing to do: origin/main is already at origin/dev (${target})."
    exit 0
fi

echo
echo "About to fast-forward main to ${target} (${count} commit(s)) and push."
echo "This DEPLOYS STAGING immediately. It does not touch production."
echo
require_confirmation "${version}" "${scope}" "${target_sha}"

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
    # Resolved here rather than up front: the rest of this script is pure git, and a gh
    # outage should not be able to block a staging deploy.
    repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null || echo '<owner>/<repo>')
    echo "       A ref update preserves the shas, but note it is subject to the same" >&2
    echo "       branch protection that just rejected the push -- it only works if you" >&2
    echo "       have bypass or admin rights on main. Omitting force is deliberate: the" >&2
    echo "       API refuses a non-fast-forward by default." >&2
    echo "         gh api -X PATCH repos/${repo}/git/refs/heads/main \\" >&2
    echo "           -f sha=$(git rev-parse origin/dev)" >&2
    echo >&2
    echo "       If you lack those rights, this needs whoever administers the branch." >&2
    exit 1
fi

if [ "${dry_run}" = "1" ]; then
    print_dry_run_footer "${scope}" "${target_sha}" \
        "scripts/release/merge-to-main.sh ${version}"
    exit 0
fi
echo
echo "Pushed. Staging is deploying. Monitor #aws-igvf-staging for batch-upgrade errors (step 10)."
