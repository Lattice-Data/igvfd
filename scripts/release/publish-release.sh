#!/bin/bash
# Step 12 of docs/staging_deploy.md: publish the GitHub Release from the tag created in
# step 9. Run this only after the Slack check (step 10) and the AWS approval (step 11).
#
# Safe to re-run: it refuses if a release for the tag already exists rather than
# duplicating it.
#
# Usage: scripts/release/publish-release.sh X.Y.Z NOTES_FILE [--yes]
set -euo pipefail

version="${1:?usage: publish-release.sh X.Y.Z NOTES_FILE [--yes]}"
notes_file="${2:?usage: publish-release.sh X.Y.Z NOTES_FILE [--yes]}"
assume_yes="${3:-}"
tag="v${version}"

cd "$(git rev-parse --show-toplevel)"

if [ ! -s "${notes_file}" ]; then
    echo "ERROR: notes file '${notes_file}' is missing or empty." >&2
    exit 1
fi

git fetch origin -p --tags

if ! git rev-parse -q --verify "refs/tags/${tag}" >/dev/null; then
    echo "ERROR: tag ${tag} does not exist. Run scripts/release/tag.sh first (step 9)." >&2
    exit 1
fi

# Derive the repo from the checkout so the release cannot be created somewhere the tag
# was never pushed.
repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
target=$(git rev-list -n1 "${tag}")

if gh release view "${tag}" --repo "${repo}" >/dev/null 2>&1; then
    echo "ERROR: a GitHub Release for ${tag} already exists on ${repo}. Nothing to do." >&2
    exit 1
fi

echo
echo "About to publish a public GitHub Release ${tag} on ${repo} at $(git rev-parse --short "${target}")."
echo
if [ "${assume_yes}" != "--yes" ]; then
    if [ ! -t 0 ]; then
        echo "ERROR: not a tty and --yes not given; refusing to publish unconfirmed." >&2
        exit 1
    fi
    read -r -p "Type the tag to confirm (${tag}): " reply
    if [ "${reply}" != "${tag}" ]; then
        echo "Aborted; nothing published." >&2
        exit 1
    fi
fi

if ! gh release create "${tag}" \
    --repo "${repo}" \
    --title "${tag}" \
    --target "${target}" \
    --notes-file "${notes_file}"; then
    echo >&2
    echo "ERROR: creating the GitHub Release failed. The tag is unaffected; retry with:" >&2
    echo "         gh release create ${tag} --repo ${repo} --title ${tag} \\" >&2
    echo "           --target ${target} --notes-file ${notes_file}" >&2
    exit 1
fi

echo
echo "Released ${tag}."
