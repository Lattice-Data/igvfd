#!/bin/bash
# Steps 11 and 12 of docs/staging_deploy.md: tag the released commit and publish the
# GitHub Release.
#
# The tag goes on main, NOT on dev. In the normal case these are the same commit, because
# step 6 fast-forwards main to dev immediately beforehand -- so this is usually a no-op.
# It only diverges if something merged to dev in between, and then main is the correct
# target: it is the commit staging actually deployed. Every tag through v11.0.0 landed on
# the version-bump commit, so this has never yet mattered in practice; it is a guard, not
# a fix for a live problem.
#
# Usage: scripts/release/tag-and-release.sh X.Y.Z /path/to/notes.md
set -euo pipefail

version="${1:?usage: tag-and-release.sh X.Y.Z NOTES_FILE}"
notes_file="${2:?usage: tag-and-release.sh X.Y.Z NOTES_FILE}"
tag="v${version}"

cd "$(git rev-parse --show-toplevel)"

if [ ! -s "${notes_file}" ]; then
    echo "ERROR: notes file '${notes_file}' is missing or empty." >&2
    exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: working tree is dirty. Commit or stash first." >&2
    exit 1
fi

git fetch origin -p --tags

if git rev-parse -q --verify "refs/tags/${tag}" >/dev/null; then
    echo "ERROR: tag ${tag} already exists locally." >&2
    exit 1
fi

git checkout main
git merge origin/main --ff-only

main_sha=$(git rev-parse HEAD)

main_version=$(sed -n "s/^__version__ = '\(.*\)'$/\1/p" src/igvfd/__init__.py)
if [ "${main_version}" != "${version}" ]; then
    echo "ERROR: main has __version__ = '${main_version}', expected '${version}'." >&2
    echo "       Refusing to tag ${tag} on a commit carrying a different version." >&2
    exit 1
fi

# Informational: dev being ahead is normal and is exactly why we tag main.
if [ "${main_sha}" != "$(git rev-parse origin/dev)" ]; then
    ahead=$(git rev-list --count main..origin/dev)
    echo "NOTE: origin/dev is ${ahead} commit(s) ahead of main. Tagging main"
    echo "      (${main_sha:0:9}), the commit that was actually deployed to staging."
    echo
fi

echo "Tagging ${tag} at ${main_sha:0:9} ($(git log -1 --pretty=%s))"
git tag -a "${tag}" -F "${notes_file}" "${main_sha}"
git push origin "refs/tags/${tag}"

gh release create "${tag}" \
    --repo Lattice-Data/igvfd \
    --title "${tag}" \
    --target "${main_sha}" \
    --notes-file "${notes_file}"

echo
echo "Released ${tag}."
