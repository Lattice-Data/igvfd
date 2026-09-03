---
name: staging-release
description: "Drive an igvfd staging release end to end, following docs/staging_deploy.md: pick the version number from what changed on dev vs main, open and track the version-bump PR, open the dev -> main PR, fast-forward main to trigger the staging deploy, then tag the deployed commit and publish the GitHub Release. Stops and hands control back at the human gates (JIRA cleanup, the Slack #aws-igvf-staging batch-upgrade check, and the AWS approve/reject). Use whenever the user wants to cut, run, or continue an igvfd release or staging deploy, bump the version for a release, tag a release, or publish release notes. Trigger on mentions of release, staging deploy, version bump, cut a release, tag vX.Y.Z, or staging_deploy.md."
---

# igvfd staging release

Automates the mechanical parts of `docs/staging_deploy.md` and stops at every step that
needs a human. The authoritative process is the doc; this skill is a faster path through
it, not a replacement. If the two ever disagree, the doc wins -- say so and stop.

## Non-negotiable rules

- **Never approve or reject the AWS release.** That is the human safety gate (step 10).
  Not automatable here anyway: no AWS credentials are configured.
- **Never skip a confirmation gate**, even if the user seems to be in a hurry. Pushing
  `main`, pushing a tag, and publishing a release are all outward-facing.
- **Stop immediately on any script error.** The scripts fail loudly and leave nothing
  half-pushed. Report the error verbatim; do not work around it.
- Steps 1 (JIRA cleanup) and 9 (Slack `#aws-igvf-staging`) are the user's to do. Remind
  them at the right moment; do not attempt them.

## Helper scripts

All three live in `scripts/release/`, are guarded, and abort rather than improvise:

| Script | Doc step | What it does |
|---|---|---|
| `preflight.sh` | -- | Read-only. Version, latest tag, dev-vs-main commits, ff-ability. |
| `merge-to-main.sh X.Y.Z` | 6 | ff-only merge of dev into main, then push. Triggers staging. |
| `tag-and-release.sh X.Y.Z NOTES` | 11, 12 | Tags **main**, pushes tag, publishes GitHub Release. |

## Phase A -- survey and pick a version

1. Run `scripts/release/preflight.sh`. If it fails, stop and report; a dirty tree or
   diverged branches must be fixed by the user.
2. Read the commits it lists. Judge minor vs. major (doc step 2). Weigh toward **major**
   when there are schema changes, new required properties, changed enums, or upgrade
   steps under `src/igvfd/upgrade/`. Check with:
   `git diff --stat origin/main..origin/dev -- src/igvfd/schemas src/igvfd/upgrade`
3. Note for context: every igvfd tag so far has been a major bump (v3 ... v11). A minor
   bump is unusual -- if you land on one, say why explicitly.
4. Remind the user of step 1: confirm the JIRA release is clean and all tickets are
   merged to `dev`. Wait for their go-ahead.
5. **Gate:** propose `X.Y.Z` with a one-line justification and get explicit agreement.
   Do not guess and proceed.

## Phase B -- version bump PR (doc step 3)

1. Branch from up-to-date `dev`, e.g. `bump-version-X.Y.Z`.
2. Edit only the `__version__` line in `src/igvfd/__init__.py`.
3. Commit as `Bump version to X.Y.Z` (matches existing history), push, and
   `gh pr create --base dev`.
4. Hand the PR URL to the user. They get it reviewed and merged; required checks are
   `igvfd-pytest`, `cdk-pytest`, `cdk-lambda-runtime-pytest`,
   `igvfd-check-opensearch-mappings`.
5. Poll with `gh pr view <PR> --json state,reviewDecision,statusCheckRollup` rather than
   asking the user to babysit it.

## Phase C -- dev to main PR (doc steps 4, 5)

1. Once the bump is on `dev`: `gh pr create --base main --head dev --title "Release vX.Y.Z"`.
2. Body: the commit list from `git log --pretty='- %s' origin/main..origin/dev`.
3. Wait for approval. Poll as in Phase B. Do not merge an unapproved PR.

## Phase D -- deploy to staging (doc steps 6, 7)

1. **Gate:** confirm with the user that the PR is approved and they want staging updated
   now. Say plainly that this deploys.
2. Run `scripts/release/merge-to-main.sh X.Y.Z`.
3. If the push is rejected by branch protection, the script says so and has pushed
   nothing. Report it and offer `gh pr merge <PR> --merge` instead. Do not force anything.
4. Tell the user staging is deploying and that step 9 is theirs: watch
   `#aws-igvf-staging` for batch-upgrade errors and dead-letter-queue messages (step 9).

## Phase E -- STOP. Human gates (doc steps 9, 10)

End the turn here. The user must:

- confirm `#aws-igvf-staging` is clean of batch-upgrade and DLQ errors, and
- approve or reject the release in AWS.

Do not poll, do not proceed, do not offer to approve. If they report errors, help
diagnose -- a rejected release does not get tagged.

## Phase F -- tag and publish (doc steps 8, 11, 12)

Only after the user confirms the AWS approval succeeded.

1. Build release notes from the commits that actually shipped:
   `git log --pretty='- %s' <last-tag>..origin/main`
   Group by JIRA ticket where the subjects carry one (`DB2-nn: ...`); keep the rest under
   a short "Other" heading. Show the user the notes and let them edit.
2. **Gate:** confirm the notes and that they want the release published.
3. Write the notes to a file and run:
   `scripts/release/tag-and-release.sh X.Y.Z <notes-file>`
4. The script tags `main`, not `dev`. Usually identical -- step 6 just fast-forwarded
   main to dev -- so this is normally a no-op. It matters only if something merged to dev
   in the meantime, and then `main` is right: it is what staging deployed. Nothing in the
   repo consumes tags (CI is branch-triggered, the app version comes from
   `src/igvfd/__init__.py`), so the tag is a human bookmark only.
5. Report the release URL.

## Resuming mid-release

Releases span the AWS gate, so the user will often come back later. Re-run
`preflight.sh` and orient from state rather than assuming:

- `origin/main` still behind `origin/dev` and no bump commit -> Phase A/B.
- Bump commit on `dev`, `main` behind -> Phase C/D.
- `main` == the bump commit, no `vX.Y.Z` tag -> Phase E/F. Ask whether AWS was approved.
- Tag exists, no GitHub Release -> just the release step.
