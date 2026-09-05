#!/bin/bash
# Step 12 of docs/staging_deploy.md: publish the GitHub Release from the tag created in
# step 9. Run this only after the Slack check (step 10) and the AWS approval (step 11).
#
# Usage: scripts/release/publish-release.sh X.Y.Z NOTES_FILE [--dry-run] [--yes|--confirm-token=X]
set -euo pipefail

# shellcheck source-path=SCRIPTDIR
source "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
parse_release_args "$@"
require_positional 2 "publish-release.sh X.Y.Z NOTES_FILE [--dry-run] [--yes|--confirm-token=X]"
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

# From origin, so the release cannot be created somewhere the tag was never pushed. See
# origin_repo in _common.sh for why 'gh repo view' does not give that guarantee.
repo=$(origin_repo)
# From the remote, so a stale local tag cannot make the confirmation line lie.
target=$(git ls-remote --tags origin "refs/tags/${tag}^{}" | cut -f1)
[ -n "${target}" ] || target=$(git ls-remote --tags origin "refs/tags/${tag}" | cut -f1)

scope="publish:${version}:$(notes_digest "${notes_file}")"

# Via gh api, matching preflight.sh: 'gh release view' cannot tell a 404 from an auth or
# network failure, and it also finds drafts that repos/.../releases/tags/X does not -- so
# using different calls here and there let the two disagree about whether step 12 was
# outstanding. A draft escapes both; 'gh release create' still refuses one.
# rc captured explicitly: under set -euo pipefail a bare failing assignment aborts the
# script, which is how the not-released branch went unreachable in preflight once already.
probe_rc=0
release_probe=$(gh api "repos/${repo}/releases/tags/${tag}" 2>&1) || probe_rc=$?
if [ "${probe_rc}" = "0" ]; then
    echo "ERROR: a GitHub Release for ${tag} already exists on ${repo}. Nothing to do." >&2
    exit 1
elif ! printf '%s' "${release_probe}" | grep -q 'HTTP 404'; then
    echo "ERROR: could not determine whether ${tag} already has a GitHub Release." >&2
    printf '       %s\n' "${release_probe}" >&2
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
