> **Automated path:** run the `staging-release` skill (`.claude/skills/staging-release/`)
> to have Claude drive steps 3-9 and 12, stopping at each human gate. The guarded helper
> scripts it calls live in `scripts/release/` and can also be run by hand. Steps 1 (JIRA),
> 10 (Slack `#aws-igvf-staging`) and 11 (AWS approve/reject) stay manual. You always pick
> the version number yourself; nothing derives it.
>
> Scripts: `preflight.sh` (survey), `merge-to-main.sh` (step 6),
> `tag.sh` (step 9), `publish-release.sh` (step 12). Each takes `--dry-run`.
> `test-release-scripts.sh` covers their guards.

1. Clean up `igvfd` JIRA release
    * Make sure all tickets merged to `dev` branch

2. Evaluate the changes on `dev` vs. `main`, and decide if the changes grant minor (non-breaking) or major (breaking) version update

3. Make a branch to update the version number to `X.Y.Z` in `igvfd/src/igvfd/__init__.py` push and make PR

4. After approval and merge of the version update branch to `dev` create PR from `dev` to `main` branch

5. After approval of the PR to `main` follow next steps

6. Merge the PR to `main`.
```
$ git checkout dev
$ git fetch origin -p
$ git pull
$ git checkout main
$ git pull
$ git merge dev --ff-only

proceed ONLY if no merge conflicts/errors encountered!

$ git push origin main
```

7. This will cause the `staging` to be updated

8. Copy the list of commits that have been merged to `main`:
```
$ git checkout main
$ git fetch origin -p
$ git pull
$ git log --pretty=%s
```

9. After choosing the commits to be included in the tag. Make the tag for version `X.Y.Z`.

    Tag the commit that is actually on `main` (the one staging is running). Do **not**
    tag `dev`: normally they are the same commit, since step 6 just fast-forwarded `main`
    to `dev`, but if anything merged to `dev` in the meantime the tag would point at
    commits that were never deployed:
```
$ git checkout main
$ git fetch origin -p
$ git pull

# verify main is what you expect before tagging:
$ git log -1 --oneline

put the details in a file rather than typing them into the editor:
$ vi /tmp/release-notes-X.Y.Z.md

# Both flags matter. Without --cleanup=whitespace, git strips every line starting
# with '#', silently deleting the markdown headings. And -F avoids the editor
# entirely: with --cleanup=whitespace git's editor template says its own '#' lines
# "will be kept", so anything left behind ends up inside the tag message.
$ git tag -a vX.Y.Z --cleanup=whitespace -F /tmp/release-notes-X.Y.Z.md
$ git push origin tags/vX.Y.Z

keep that file: step 12 needs the same text.
```

10. Monitor batch-upgrade errors and messages in slack channel #aws-igvf-staging

proceed ONLY if there are no batch-upgrade errors, and if there are no errors (Like dead letter queue) in the slack channel

11. approve release on AWS or reject it in case there were problems

    Note what this approval actually does: pushing `main` in step 6 already deployed
    `staging` unconditionally. The `ProductionDeploymentManualApprovalStep` is the `pre`
    step on `ProductionAndSandboxDeployWave`
    (`cdk/infrastructure/constructs/pipeline.py`), so approving here promotes the release
    to **production and sandbox**. Rejecting leaves staging as it is -- it does not roll
    staging back.

12. On Github `Make a Release` from the tag, pasting the proper commits in the details.
