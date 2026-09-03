#!/bin/bash
# Step 9 of docs/staging_deploy.md: tag the commit that was deployed to staging.
#
# The tag goes on main, NOT on dev. In the normal case these are the same commit, because
# step 6 fast-forwards main to dev immediately beforehand -- so this is usually a no-op.
# It only diverges if something merged to dev in between, and then main is the correct
# target: it is the commit staging actually deployed.
#
# The GitHub Release is step 12, after the Slack check and the AWS approval. It is a
# separate script (publish-release.sh) so those two human gates sit between them.
#
# Safe to re-run: if the tag already exists at the right commit, it just pushes it.
#
# Usage: scripts/release/tag.sh X.Y.Z NOTES_FILE [--yes] [--dry-run]
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
parse_release_args "$@"
version="${POSITIONAL[0]:?usage: tag.sh X.Y.Z NOTES_FILE [--yes] [--dry-run]}"
notes_file="${POSITIONAL[1]:?usage: tag.sh X.Y.Z NOTES_FILE [--yes] [--dry-run]}"
tag="v${version}"

# Resolve before the cd, or a relative path from a subdirectory is reported as missing.
notes_file=$(cd "$(dirname "${notes_file}")" 2>/dev/null && printf '%s/%s' "$(pwd)" "$(basename "${notes_file}")") \
    || { echo "ERROR: notes file '${POSITIONAL[1]}' does not resolve." >&2; exit 1; }

cd "$(git rev-parse --show-toplevel)"
start_ref=$(current_ref)
restore_ref() { git checkout -q "${start_ref}" 2>/dev/null || true; }
trap restore_ref EXIT

if [ ! -s "${notes_file}" ]; then
    echo "ERROR: notes file '${notes_file}' is missing or empty." >&2
    exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: working tree is dirty. Commit or stash first." >&2
    exit 1
fi

git fetch origin -p --tags

git checkout main
git merge origin/main --ff-only
main_sha=$(git rev-parse HEAD)
short_sha=$(git rev-parse --short HEAD)

main_version=$(read_version_from main)
if [ "${main_version}" != "${version}" ]; then
    echo "ERROR: main has __version__ = '${main_version}', expected '${version}'." >&2
    echo "       Refusing to tag ${tag} on a commit carrying a different version." >&2
    exit 1
fi

# Informational: dev being ahead is normal and is exactly why we tag main.
if git merge-base --is-ancestor main origin/dev && [ "${main_sha}" != "$(git rev-parse origin/dev)" ]; then
    echo "NOTE: origin/dev is $(git rev-list --count main..origin/dev) commit(s) ahead of"
    echo "      main. Tagging main (${short_sha}), the commit deployed to staging."
    echo
fi

if git rev-parse -q --verify "refs/tags/${tag}" >/dev/null; then
    existing=$(git rev-list -n1 "${tag}")
    if [ "${existing}" != "${main_sha}" ]; then
        echo "ERROR: tag ${tag} already exists at $(git rev-parse --short "${existing}"), not at" >&2
        echo "       main (${short_sha}). Delete it deliberately ('git tag -d ${tag}') first." >&2
        exit 1
    fi
    echo "Tag ${tag} already exists at ${short_sha}; pushing it."
else
    echo
    echo "About to tag ${tag} at ${short_sha} ($(git log -1 --pretty=%s)) and push it."
    echo
    require_confirmation "${tag}"
    run git tag -a "${tag}" -F "${notes_file}" "${main_sha}"
fi

if ! run git push origin "refs/tags/${tag}"; then
    echo >&2
    echo "ERROR: pushing ${tag} failed. The tag exists locally only. Either retry, or" >&2
    echo "       remove it with 'git tag -d ${tag}' before trying again." >&2
    exit 1
fi

echo
if [ "${dry_run}" = "1" ]; then
    echo "Dry run complete. Every guard passed; nothing was tagged or pushed."
    exit 0
fi
echo "Tagged ${tag} at ${short_sha}."
echo "Next: step 10 (#aws-igvf-staging), step 11 (AWS approval -> production/sandbox),"
echo "then step 12: scripts/release/publish-release.sh ${version} ${notes_file}"
