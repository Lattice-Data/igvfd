#!/bin/bash
# Step 9 of docs/staging_deploy.md: tag the commit that was deployed to staging.
#
# The tag goes on main, NOT on dev. In the normal case these are the same commit, because
# step 6 fast-forwards main to dev immediately beforehand -- so this is usually a no-op.
# It only diverges if something merged to dev in between, and then main is the correct
# target: it is the commit staging actually deployed.
#
# Nothing is checked out: the tag is created directly on origin/main's commit, so the
# working tree and the current branch are untouched and --dry-run really does nothing.
#
# The GitHub Release is step 12, after the Slack check and the AWS approval. It is a
# separate script (publish-release.sh) so those two human gates sit between them.
#
# Usage: scripts/release/tag.sh X.Y.Z NOTES_FILE [--dry-run] [--yes|--confirm-token=X]
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
parse_release_args "$@"
version="${POSITIONAL[0]:?usage: tag.sh X.Y.Z NOTES_FILE [--dry-run] [--yes|--confirm-token=X]}"
notes_file="${POSITIONAL[1]:?usage: tag.sh X.Y.Z NOTES_FILE [--dry-run] [--yes|--confirm-token=X]}"
expect_positional_count 2
tag="v${version}"

notes_file=$(resolve_path "${notes_file}") \
    || { echo "ERROR: notes file '${POSITIONAL[1]}' does not resolve." >&2; exit 1; }

cd "$(git rev-parse --show-toplevel)"

if [ ! -s "${notes_file}" ]; then
    echo "ERROR: notes file '${notes_file}' is missing or empty." >&2
    exit 1
fi

# Untracked files are tolerated: nothing here touches the working tree anyway.
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    echo "ERROR: working tree has uncommitted changes. Commit or stash first." >&2
    exit 1
fi

git fetch origin -p --tags

main_sha=$(git rev-parse origin/main)
short_sha=$(git rev-parse --short origin/main)

main_version=$(read_version_from origin/main)
if [ "${main_version}" != "${version}" ]; then
    echo "ERROR: origin/main has __version__ = '${main_version}', expected '${version}'." >&2
    echo "       Refusing to tag ${tag} on a commit carrying a different version." >&2
    exit 1
fi

# Informational: dev being ahead is normal and is exactly why we tag main.
if [ "${main_sha}" != "$(git rev-parse origin/dev)" ] \
   && git merge-base --is-ancestor origin/main origin/dev; then
    echo "NOTE: origin/dev is $(git rev-list --count origin/main..origin/dev) commit(s) ahead"
    echo "      of main. Tagging main (${short_sha}), the commit deployed to staging."
    echo
fi

tag_exists=0
if git rev-parse -q --verify "refs/tags/${tag}" >/dev/null; then
    existing=$(git rev-list -n1 "${tag}")
    if [ "${existing}" != "${main_sha}" ]; then
        echo "ERROR: tag ${tag} already exists at $(git rev-parse --short "${existing}"), not at" >&2
        echo "       main (${short_sha}). Delete it deliberately ('git tag -d ${tag}') first." >&2
        exit 1
    fi
    tag_exists=1
    echo "Tag ${tag} already exists locally at ${short_sha}."
fi

echo
echo "About to tag ${tag} at ${short_sha} ($(git log -1 --pretty=%s "${main_sha}")) and push it."
echo
# Before any side effect, including the re-run path where the tag already exists: pushing
# a tag is outward-facing either way.
require_confirmation "${tag}" "tag:${version}" "${main_sha}"

if [ "${tag_exists}" = "0" ]; then
    # --cleanup=whitespace, because git tag defaults to 'strip', which discards every
    # line starting with '#' -- i.e. every markdown heading in the release notes. The
    # default silently shrinks the notes, makes the tag disagree with the GitHub Release
    # (built from the file, not the tag), and in the all-headings case leaves the tag
    # message empty.
    run git tag -a "${tag}" --cleanup=whitespace -F "${notes_file}" "${main_sha}"
fi

if ! run git push origin "refs/tags/${tag}"; then
    echo >&2
    echo "ERROR: pushing ${tag} failed. The tag exists locally only. Either retry, or" >&2
    echo "       remove it with 'git tag -d ${tag}' before trying again." >&2
    exit 1
fi

if [ "${dry_run}" = "1" ]; then
    print_dry_run_footer "tag:${version}" "${main_sha}" \
        "scripts/release/tag.sh ${version} ${notes_file}"
    exit 0
fi

echo
echo "Tagged ${tag} at ${short_sha}."
echo "Next: step 10 (#aws-igvf-staging), step 11 (AWS approval -> production/sandbox),"
echo "then step 12: scripts/release/publish-release.sh ${version} ${notes_file}"
