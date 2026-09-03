# Shared helpers for the release scripts. Sourced, not executed.

# --yes and --dry-run in any position, so 'merge-to-main.sh --yes 12.0.0' works too.
# Sets: assume_yes, dry_run, and POSITIONAL (the non-flag arguments).
parse_release_args() {
    assume_yes=0
    dry_run=0
    POSITIONAL=()
    while [ $# -gt 0 ]; do
        case "$1" in
            --yes) assume_yes=1 ;;
            --dry-run) dry_run=1 ;;
            -*) echo "ERROR: unknown flag '$1'" >&2; exit 1 ;;
            *) POSITIONAL+=("$1") ;;
        esac
        shift
    done
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

# --abbrev-ref prints the literal 'HEAD' when detached, which would make the restore trap
# quietly leave the operator somewhere else. Fall back to the sha so restore still works.
current_ref() {
    git symbolic-ref -q --short HEAD || git rev-parse HEAD
}

# Asks the operator to type a value back. Not reachable when stdin is not a tty; callers
# must have handled that case already.
confirm_by_typing() {
    local expected="$1" reply
    read -r -p "Type ${expected} to confirm: " reply
    if [ "${reply}" != "${expected}" ]; then
        echo "Aborted." >&2
        exit 1
    fi
}

# The confirmation gate. A human at a terminal is prompted. A non-interactive caller (an
# agent running this through a tool, CI) must pass --yes, which means the confirmation
# happened elsewhere -- in conversation, where the operator also approved this very
# command. Under --dry-run nothing happens, so no confirmation is needed.
require_confirmation() {
    local expected="$1"
    [ "${dry_run}" = "1" ] && return 0
    [ "${assume_yes}" = "1" ] && return 0
    if [ ! -t 0 ]; then
        echo "ERROR: stdin is not a tty and --yes was not given." >&2
        echo "       Re-run with --yes once the operator has confirmed this step, or run" >&2
        echo "       --dry-run first to see exactly what would happen." >&2
        exit 1
    fi
    confirm_by_typing "${expected}"
}

read_version_from() {
    local v
    v=$(git show "$1:src/igvfd/__init__.py" | sed -n "s/^__version__ = '\(.*\)'\$/\1/p")
    if [ -z "${v}" ]; then
        echo "ERROR: could not parse __version__ from $1:src/igvfd/__init__.py" >&2
        exit 1
    fi
    printf '%s' "${v}"
}
