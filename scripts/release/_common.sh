# shellcheck shell=bash
# Shared helpers for the release scripts. Sourced, not executed.

# --yes, --dry-run and --confirm-token=X in any position, so 'merge-to-main.sh --yes
# 12.0.0' works too. Sets: assume_yes, dry_run, confirm_token, POSITIONAL.
parse_release_args() {
    assume_yes=0
    dry_run=0
    confirm_token=
    POSITIONAL=()
    while [ $# -gt 0 ]; do
        case "$1" in
            --yes) assume_yes=1 ;;
            --dry-run) dry_run=1 ;;
            --confirm-token=*) confirm_token="${1#*=}" ;;
            -*) echo "ERROR: unknown flag '$1'" >&2; exit 1 ;;
            *) POSITIONAL+=("$1") ;;
        esac
        shift
    done
}

# ${POSITIONAL[0]:?usage} does not work on bash 3.2 (macOS's default /bin/bash): under
# set -u an empty array subscript raises 'POSITIONAL[0]: unbound variable' before the
# :?-message is reached, so the caller sees a shell error instead of usage. Callers use
# this instead.
require_positional() {
    local n="$1" usage="$2"
    if [ "${#POSITIONAL[@]}" -lt "${n}" ]; then
        echo "usage: ${usage}" >&2
        exit 1
    fi
}

# A flag that lost its leading dashes lands in POSITIONAL and would otherwise be ignored.
expect_positional_count() {
    if [ "${#POSITIONAL[@]}" -gt "$1" ]; then
        echo "ERROR: unexpected extra argument '${POSITIONAL[$1]}'." >&2
        exit 1
    fi
}

# Resolve a path before any cd to the repo root, so relative paths given from a
# subdirectory still work. CDPATH='' because a set CDPATH makes cd echo to stdout.
resolve_path() {
    local dir base
    dir=$(CDPATH='' cd -- "$(dirname -- "$1")" 2>/dev/null && pwd) || return 1
    base=$(basename -- "$1")
    printf '%s/%s' "${dir}" "${base}"
}

# Runs a side-effecting command, or prints it under --dry-run. Every push, tag and
# release call goes through this, so --dry-run exercises all the guards above it.
run() {
    if [ "${dry_run}" = "1" ]; then
        echo "DRY RUN: $*"
    else
        "$@"
    fi
}

# --abbrev-ref prints the literal 'HEAD' when detached, which would make a restore trap
# quietly leave the operator somewhere else. Fall back to the sha so restore still works.
current_ref() {
    git symbolic-ref -q --short HEAD || git rev-parse HEAD
}

read_version_from() {
    local contents v
    # git show is captured on its own rather than piped straight into sed: in a pipeline
    # its failure would trip pipefail and abort the caller with a bare git error, so the
    # message below would never be reached.
    if ! contents=$(git show "$1:src/igvfd/__init__.py" 2>/dev/null); then
        if ! git rev-parse -q --verify "$1" >/dev/null 2>&1; then
            # Distinguished because a single-branch clone lacking origin/dev is a very
            # different problem from the file having moved.
            echo "ERROR: no such ref '$1'. A single-branch clone may not have it; try" >&2
            echo "       'git remote set-branches --add origin dev && git fetch origin'." >&2
        else
            echo "ERROR: cannot read src/igvfd/__init__.py at '$1'." >&2
        fi
        exit 1
    fi
    # sed -n exits 0 on no match, so an unparsed version would otherwise sail through as
    # an empty string and compare equal to another empty string.
    v=$(printf '%s\n' "${contents}" | sed -n "s/^__version__ = '\(.*\)'\$/\1/p")
    if [ -z "${v}" ]; then
        echo "ERROR: could not parse __version__ from '$1':src/igvfd/__init__.py" >&2
        exit 1
    fi
    printf '%s' "${v}"
}

# Ties a confirmation to one exact action on one exact commit, so that a target which
# moves between the dry run and the real run invalidates the confirmation.
#
# It does NOT prove the dry run happened: this is a plain hash of two values the caller
# already knows, with no secret and no stored state, so anyone can compute it directly.
# Treat it as a target-moved check, nothing more.
release_token() {
    printf '%s:%s' "$1" "$2" | sha256_hex | cut -c1-8
}

# sha256 of stdin as hex. sha256sum on most Linux images, shasum on macOS. Neither is
# universal.
sha256_hex() {
    if command -v shasum >/dev/null 2>&1; then
        shasum -a 256
    elif command -v sha256sum >/dev/null 2>&1; then
        sha256sum
    else
        echo "ERROR: need shasum or sha256sum to compute a digest." >&2
        exit 1
    fi
}

# Short digest of the notes file, folded into the confirmation scope by the two scripts
# that take one. Without it the token covers the action and the target sha but not the
# notes, so a token minted against one set of notes is accepted for another -- and
# confirming the notes is itself one of the human gates. The cost is intended: editing
# the notes invalidates the token, which is what makes the second gate mean something.
notes_digest() {
    sha256_hex < "$1" | cut -c1-8
}

# The confirmation gate.
#
#   at a terminal   -- type the value back (or --yes to skip the prompt)
#   non-interactive -- must pass --confirm-token for this action and this commit
#
# Be clear about what the non-interactive path is worth. The token is computable without
# running --dry-run, so it does not force the dry run to happen; it only fails when the
# target has moved. Nothing checked inside a script can gate the caller that invokes it.
# The real gate is the operator approving the command, and an agent driving these scripts
# is trusted to run --dry-run first and show the output.
require_confirmation() {
    local expected="$1" scope="$2" sha="$3" token reply
    [ "${dry_run}" = "1" ] && return 0
    token=$(release_token "${scope}" "${sha}")

    if [ -n "${confirm_token}" ]; then
        if [ "${confirm_token}" = "${token}" ]; then
            return 0
        fi
        echo "ERROR: --confirm-token does not match this action." >&2
        echo "       The target has probably moved since the dry run. Re-run --dry-run." >&2
        exit 1
    fi

    if [ ! -t 0 ]; then
        echo "ERROR: stdin is not a tty, so there is no way to confirm interactively." >&2
        echo "       Re-run with --dry-run, show the operator what it would do, and once" >&2
        echo "       they agree re-run with the --confirm-token it prints." >&2
        echo "       Do not reach for --yes to get past this message." >&2
        exit 1
    fi

    [ "${assume_yes}" = "1" ] && return 0
    read -r -p "Type ${expected} to confirm: " reply
    if [ "${reply}" != "${expected}" ]; then
        echo "Aborted." >&2
        exit 1
    fi
}

# Closing line for a dry run: how to actually do it.
print_dry_run_footer() {
    local scope="$1" sha="$2" cmd="$3"
    echo
    echo "Dry run complete. Every guard passed; nothing was changed."
    echo "To perform it for real:"
    printf '  %s --confirm-token=%s\n' "${cmd}" "$(release_token "${scope}" "${sha}")"
}


# owner/repo from origin's URL. Deliberately not 'gh repo view': that uses gh's base-repo
# resolution, which prefers the parent for a fork and is overridden outright by GH_REPO --
# so it can name a repo the tag was never pushed to, and since forks share object storage
# a release against it can succeed. Everything else in these scripts talks to origin, so
# this keeps the gh calls pointed at the same place as the git ones.
origin_repo() {
    local url slug
    url=$(git remote get-url origin) || return 1
    slug=$(printf '%s' "${url}" | sed -E 's#^(https?://[^/]+/|ssh://[^/]+/|[^@]+@[^:]+:)##; s#/*$##; s#\.git$##')
    # ':' rejected too: an scp-style remote with no user (github.com:owner/repo, valid
    # with an ssh config alias) survives the substitutions above and would otherwise pass
    # as the slug 'github.com:owner/repo'.
    if printf '%s' "${slug}" | grep -q ':' || ! printf '%s' "${slug}" | grep -Eq '^[^/]+/[^/]+$'; then
        echo "ERROR: could not derive owner/repo from origin URL '${url}'." >&2
        return 1
    fi
    printf '%s' "${slug}"
}
