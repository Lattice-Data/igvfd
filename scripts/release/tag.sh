#!/bin/bash
# Step 9 of docs/staging_deploy.md: tag the commit that was deployed to staging.
#
# The tag goes on main, NOT on dev. In the normal case these are the same commit, because
# step 6 fast-forwards main to dev immediately beforehand -- so this is usually a no-op.
# It only diverges if something merged to dev in between, and then main is the correct
# target: it is the commit staging actually deployed. Every tag through v11.0.0 landed on
# the version-bump commit, so this has never yet mattered in practice; it is a guard, not
# a fix for a live problem.
#
# The GitHub Release is step 12, after the Slack check and the AWS approval. It is a
# separate script (publish-release.sh) so those two human gates sit between them.
#
# Safe to re-run: if the tag already exists at the right commit, it just pushes it.
#
# Usage: scripts/release/tag.sh X.Y.Z NOTES_FILE [--yes]
set -euo pipefail

version="${1:?usage: tag.sh X.Y.Z NOTES_FILE [--yes]}"
notes_file="${2:?usage: tag.sh X.Y.Z NOTES_FILE [--yes]}"
assume_yes="${3:-}"
tag="v${version}"

cd "$(git rev-parse --show-toplevel)"
start_branch=$(git rev-parse --abbrev-ref HEAD)
restore_branch() { git checkout -q "${start_branch}" 2>/dev/null || true; }
trap restore_branch EXIT

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

main_version=$(sed -n "s/^__version__ = '\(.*\)'$/\1/p" src/igvfd/__init__.py)
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
    if [ "${assume_yes}" != "--yes" ]; then
        if [ ! -t 0 ]; then
            echo "ERROR: not a tty and --yes not given; refusing to tag unconfirmed." >&2
            exit 1
        fi
        read -r -p "Type the tag to confirm (${tag}): " reply
        if [ "${reply}" != "${tag}" ]; then
            echo "Aborted; nothing tagged." >&2
            exit 1
        fi
    fi
    git tag -a "${tag}" -F "${notes_file}" "${main_sha}"
fi

if ! git push origin "refs/tags/${tag}"; then
    echo >&2
    echo "ERROR: pushing ${tag} failed. The tag exists locally only. Either retry, or" >&2
    echo "       remove it with 'git tag -d ${tag}' before trying again." >&2
    exit 1
fi

echo
echo "Tagged ${tag} at ${short_sha}."
echo "Next: step 10 (#aws-igvf-staging), step 11 (AWS approval -> production/sandbox),"
echo "then step 12: scripts/release/publish-release.sh ${version} ${notes_file}"
