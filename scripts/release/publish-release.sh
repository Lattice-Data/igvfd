#!/bin/bash
# Step 12 of docs/staging_deploy.md: publish the GitHub Release from the tag created in
# step 9. Run this only after the Slack check (step 10) and the AWS approval (step 11).
#
# Usage: scripts/release/publish-release.sh X.Y.Z NOTES_FILE [--dry-run] [--yes|--confirm-token=X]
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
parse_release_args "$@"
version="${POSITIONAL[0]:?usage: publish-release.sh X.Y.Z NOTES_FILE [--dry-run] [--yes|--confirm-token=X]}"
notes_file="${POSITIONAL[1]:?usage: publish-release.sh X.Y.Z NOTES_FILE [--dry-run] [--yes|--confirm-token=X]}"
expect_positional_count 2
tag="v${version}"

notes_file=$(resolve_path "${notes_file}") \
    || { echo "ERROR: notes file '${POSITIONAL[1]}' does not resolve." >&2; exit 1; }

cd "$(git rev-parse --show-toplevel)"

if [ ! -s "${notes_file}" ]; then
    echo "ERROR: notes file '${notes_file}' is missing or empty." >&2
    exit 1
fi

git fetch origin -p --tags

# Check the remote, not local refs. A tag that exists only locally -- exactly the state
# tag.sh reports when its push fails -- would otherwise pass, and 'gh release create
# --target <sha>' would then create a LIGHTWEIGHT tag on the remote, silently discarding
# the annotated tag's message.
if ! git ls-remote --exit-code --tags origin "refs/tags/${tag}" >/dev/null 2>&1; then
    echo "ERROR: tag ${tag} does not exist on origin." >&2
    if git rev-parse -q --verify "refs/tags/${tag}" >/dev/null; then
        echo "       It exists locally but was never pushed. Push it first:" >&2
        echo "         git push origin refs/tags/${tag}" >&2
    else
        echo "       Run scripts/release/tag.sh first (step 9)." >&2
    fi
    exit 1
fi

# Derive the repo from the checkout so the release cannot be created somewhere the tag
# was never pushed.
repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
# From the remote, so a stale local tag cannot make the confirmation line lie.
target=$(git ls-remote --tags origin "refs/tags/${tag}^{}" | cut -f1)
[ -n "${target}" ] || target=$(git ls-remote --tags origin "refs/tags/${tag}" | cut -f1)

scope="publish:${version}"

if gh release view "${tag}" --repo "${repo}" >/dev/null 2>&1; then
    echo "ERROR: a GitHub Release for ${tag} already exists on ${repo}. Nothing to do." >&2
    exit 1
fi

echo
echo "About to publish a public GitHub Release ${tag} on ${repo} at $(git rev-parse --short "${target}")."
echo
require_confirmation "${tag}" "${scope}" "${target}"

if ! run gh release create "${tag}" \
    --repo "${repo}" \
    --title "${tag}" \
    --target "${target}" \
    --notes-file "${notes_file}"; then
    echo >&2
    echo "ERROR: creating the GitHub Release failed. The tag is unaffected; retry with:" >&2
    echo "         gh release create ${tag} --repo ${repo} --title ${tag} \\" >&2
    echo "           --target ${target} --notes-file '${notes_file}'" >&2
    exit 1
fi

if [ "${dry_run}" = "1" ]; then
    print_dry_run_footer "${scope}" "${target}" \
        "scripts/release/publish-release.sh ${version} '${notes_file}'"
    exit 0
fi
echo
echo "Released ${tag}."
