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

# shellcheck source-path=SCRIPTDIR
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
parse_release_args "$@"
require_positional 2 "tag.sh X.Y.Z NOTES_FILE [--dry-run] [--yes|--confirm-token=X]"
version="${POSITIONAL[0]}"
notes_file="${POSITIONAL[1]}"
expect_positional_count 2
tag="v${version}"

notes_file=$(resolve_path "${notes_file}") \
    || { echo "ERROR: notes file '${POSITIONAL[1]}' does not resolve." >&2; exit 1; }

cd "$(git rev-parse --show-toplevel)"

# -f as well as -s: resolve_path succeeds on a directory and -s is true for a non-empty
# one, so without this a directory argument gets through and fails later inside git.
if [ ! -f "${notes_file}" ] || [ ! -r "${notes_file}" ] || [ ! -s "${notes_file}" ]; then
    echo "ERROR: notes file '${notes_file}' is not a readable, non-empty file." >&2
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

scope="tag:${version}:$(notes_digest "${notes_file}")"
tag_exists=0
# Ask the remote first. This branch exists to recover a run whose push failed, i.e. a
# local-only tag -- but the 'git fetch -p --tags' above pulls every origin tag into
# refs/tags/, so a local check alone cannot tell the two apart. Getting that wrong is
# costly in both directions: an origin tag at main's commit would be reported as a
# successful re-tag of a release that already shipped, and an origin tag elsewhere would
# be met with a 'git tag -d' hint that re-fetches on the next run (so it never clears)
# and points the operator at deleting a published tag.
if git ls-remote --exit-code --tags origin "refs/tags/${tag}" >/dev/null 2>&1; then
    echo "ERROR: tag ${tag} exists on origin, so ${version} looks already released." >&2
    echo "       Refusing to re-tag. If this is genuinely wrong, the published tag has to" >&2
    echo "       be dealt with as a deliberate, separate decision -- not as part of a" >&2
    echo "       release run." >&2
    exit 1
fi

# Local-only from here, which is the case the recovery hint below correctly describes.
if git rev-parse -q --verify "refs/tags/${tag}" >/dev/null; then
    existing=$(git rev-list -n1 "${tag}")
    if [ "${existing}" != "${main_sha}" ]; then
        echo "ERROR: local tag ${tag} exists at $(git rev-parse --short "${existing}"), not at" >&2
        echo "       main (${short_sha}). It is not on origin, so deleting it is safe:" >&2
        echo "       'git tag -d ${tag}', then re-run." >&2
        exit 1
    fi
    tag_exists=1
    echo "Tag ${tag} already exists locally at ${short_sha}, not yet on origin."
fi

echo
echo "About to tag ${tag} at ${short_sha} ($(git log -1 --pretty=%s "${main_sha}")) and push it."
echo
# Before any side effect, including the re-run path where the tag already exists: pushing
# a tag is outward-facing either way.
require_confirmation "${tag}" "${scope}" "${main_sha}"

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
    print_dry_run_footer "${scope}" "${main_sha}" \
        "scripts/release/tag.sh ${version} '${notes_file}'"
    exit 0
fi

echo
echo "Tagged ${tag} at ${short_sha}."
echo "Next: step 10 (#aws-igvf-staging), step 11 (AWS approval -> production/sandbox),"
echo "then step 12: scripts/release/publish-release.sh ${version} '${notes_file}'"
