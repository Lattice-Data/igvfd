---
name: staging-release
description: "Drive an igvfd staging release end to end, following docs/staging_deploy.md: survey what changed on dev vs main so the human can choose the version number, open and track the version-bump PR, open the dev -> main PR, fast-forward main to deploy staging, tag the deployed commit, and publish the GitHub Release. Never chooses the version number itself, and stops at every human gate (JIRA cleanup, the Slack #aws-igvf-staging batch-upgrade check, and the AWS approve/reject that promotes to production). Use whenever the user wants to cut, run, or continue an igvfd release or staging deploy, bump the version for a release, tag a release, or publish release notes. Trigger on mentions of release, staging deploy, version bump, cut a release, tag vX.Y.Z, or staging_deploy.md."
---

# igvfd staging release

Automates the mechanical parts of `docs/staging_deploy.md` and stops at every step that
needs a human. The authoritative process is the doc; this skill is a faster path through
it, not a replacement. If the two ever disagree, the doc wins -- say so and stop.

## Non-negotiable rules

- **Never choose the version number.** See Phase A. The human states it; you never infer,
  default to, or proceed on an unanswered version.
- **Never approve or reject the AWS release.** Note what it does: pushing `main` (step 6)
  deploys staging unconditionally. The `ManualApprovalStep` is `pre=` on
  `ProductionAndSandboxDeployWave` (`cdk/infrastructure/constructs/pipeline.py`), so
  approving promotes to **production and sandbox**. That is emphatically a human's call.
- **Never skip a confirmation gate**, even if the user seems to be in a hurry. Pushing
  `main`, pushing a tag, and publishing a release are all outward-facing.

  How this works when *you* run the scripts: stdin is not a tty, so the interactive
  prompt cannot reach the user. The scripts require a `--confirm-token` instead, and the
  only place to get one is a `--dry-run` of that same action against that same commit.
  So the sequence is fixed:

  1. Run with `--dry-run`.
  2. Show the user its output -- the exact commands, and what they would change.
  3. Get an explicit yes for that specific step.
  4. Re-run with the `--confirm-token=` the dry run printed.

  `--yes` does not work without a tty; do not go looking for a way around the token. If
  the token is rejected the target moved since the dry run, so start again at step 1.
  A human running these by hand gets the real typed prompt and never needs a token.
- **Stop immediately on any script error.** The scripts fail loudly and leave nothing
  half-pushed. Report the error verbatim; do not work around it.
- Steps 1 (JIRA cleanup) and 10 (Slack `#aws-igvf-staging`) are the user's to do. Remind
  them at the right moment; do not attempt them.

## Helper scripts

All live in `scripts/release/`, are guarded, and abort rather than improvise. Each
side-effecting one confirms interactively unless given `--yes`:

| Script | Doc step | What it does |
|---|---|---|
| `preflight.sh` | -- | Read-only. Versions on main and dev, latest tag, **which step is next**, pending commits. |
| `merge-to-main.sh X.Y.Z` | 6 | ff-only merge of dev into main, then push. Deploys staging. |
| `tag.sh X.Y.Z NOTES` | 9 | Tags **main** and pushes the tag. |
| `publish-release.sh X.Y.Z NOTES` | 12 | Publishes the GitHub Release from that tag. |

The three side-effecting ones take `--dry-run` (runs every guard, prints the commands it
would run and a `--confirm-token`, changes nothing). `_common.sh` holds the shared
argument parsing and confirmation logic and is sourced, not run.
`test-release-scripts.sh` covers the phase detection and the guards; run it after
changing any of them.

## Phase A -- survey, then the human picks the version

The version number is the human's decision. Your job is to give them what they need to
make it, not to make it for them.

1. Run `scripts/release/preflight.sh`. If it fails, stop and report; a dirty tree or
   diverged branches must be fixed by the user.
2. Summarise what changed so the choice is informed. Call out anything breaking:
   `git diff --stat origin/main..origin/dev -- src/igvfd/schemas src/igvfd/upgrade`
   Schema changes, new required properties, changed enums, or new steps under
   `src/igvfd/upgrade/` all point at a major bump. Say which of these you found.
3. State the facts that bear on the choice: the current version, and that every igvfd tag
   so far has been a major bump (v3 ... v11).
4. Remind the user of step 1: confirm the JIRA release is clean and all tickets are
   merged to `dev`.
5. **Hard gate.** Ask the user outright which version to release, and stop. Do not name a
   single number as "the" answer, do not say "I'll use X unless you object", and do not
   continue on silence or on a vague reply like "sounds good". You may lay out what the
   options would be (e.g. "12.0.0 if you read the enum change as breaking, 11.1.0 if
   not") -- but the human has to pick one and say it. If they ask you to decide, tell
   them the release process requires them to make the call, and give them the evidence
   again.

Everything downstream takes the version as an explicit argument. Nothing derives it.

## Phase B -- version bump PR (doc step 3)

1. Branch from up-to-date `dev`, e.g. `bump-version-X.Y.Z`.
2. Edit only the `__version__` line in `src/igvfd/__init__.py`.
3. Commit as `Bump version to X.Y.Z` (matches existing history), push, and
   `gh pr create --base dev`.
4. Hand the PR URL to the user. Which checks are *required* lives in branch protection,
   not in the checkout, so read the PR's own status rollup rather than trusting a list
   written down here.
5. Poll with `gh pr view <PR> --json state,reviewDecision,statusCheckRollup` rather than
   asking the user to babysit it.

## Phase C -- dev to main PR (doc steps 4, 5)

1. Once the bump is on `dev`: `gh pr create --base main --head dev --title "Release vX.Y.Z"`.
2. Body: the commit list from `git log --pretty='- %s' origin/main..origin/dev`.
3. Wait for approval. Poll as in Phase B. Do not merge an unapproved PR.

## Phase D -- deploy staging (doc steps 6, 7)

1. **Gate:** confirm with the user that the PR is approved and they want staging updated
   now. Say plainly that this deploys staging immediately.
2. Run `scripts/release/merge-to-main.sh X.Y.Z`.
3. If the push is rejected by branch protection, the script says so and has pushed
   nothing. Report it, and do **not** reach for `gh pr merge`: `--merge` adds a merge
   commit and `--rebase` rewrites the shas, and either one stops `main` being a
   fast-forward of `dev`, which breaks every later release until `main` is merged back
   into `dev`. The script prints a `gh api -X PATCH .../git/refs/heads/main` command that
   moves the ref while preserving the shas. That is a direct write to `main`; hand it to
   the user rather than running it yourself.

## Phase E -- tag (doc steps 8, 9)

1. Build release notes from the commits that shipped:
   `git log --pretty='- %s' <last-tag>..origin/main`
   Group by JIRA ticket where the subjects carry one (`DB2-nn: ...`); keep the rest under
   a short "Other" heading. Show the user the notes and let them edit.
2. **Gate:** confirm the notes.
3. Write the notes **outside the working tree** -- `"$(git rev-parse --git-dir)"/release-notes-X.Y.Z.md`
   is a good spot. A notes file inside the checkout is untracked clutter that step 12
   will still need two human gates later, and it will show up in every `git status` the
   user runs in between.
4. Run `scripts/release/tag.sh X.Y.Z <notes-file>` (dry run first, per the rules above).
5. Keep the notes file; step 12 needs it.

## Phase F -- STOP. Human gates (doc steps 10, 11)

End the turn here. The user must:

- confirm `#aws-igvf-staging` is clean of batch-upgrade and dead-letter-queue errors, and
- approve or reject in AWS, which promotes to **production and sandbox**.

Do not poll, do not proceed, do not offer to approve. If they report errors, help
diagnose. Note that rejecting does not roll staging back -- staging is already deployed,
and the tag from step 9 already reflects it.

## Phase G -- publish the release (doc step 12)

Only after the user says the AWS step is done.

1. Run `scripts/release/publish-release.sh X.Y.Z <notes-file>`.
2. Report the release URL.

## Resuming mid-release

Releases span human gates, so the user will often come back later. Re-run `preflight.sh`
and orient from what it reports rather than assuming. It prints a `NEXT:` line naming the
runbook step, worked out from the versions on `origin/main` and `origin/dev` *and* the
latest tag -- the tag matters, because right after step 6 both branches carry the new
version and that is otherwise indistinguishable from no bump having happened.

One thing `preflight.sh` cannot know: whether the AWS approval has happened. If it reports
step 12, ask.

Never re-derive the version from the repo when resuming without confirming it with the
user first.
