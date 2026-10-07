---
name: hr-git-workflow
description: Use when preparing commits, publishing branches, or rewriting approved Git history in this repository.
---

# HR Git workflow

## Commit message rules

- Keep the subject at most 50 characters, including any conventional prefix.
- Use an imperative subject with a focused description of the change.
- Separate the subject and body with one blank line.
- Wrap every body line at at most 70 characters, including spaces.
- Explain what changed and why; do not repeat the entire diff.
- Do not add a Copilot co-author signature or trailer to commits.

Validate the exact message before committing, not a paraphrase. In PowerShell,
store the complete proposed message in `$message`, then run:

```powershell
$lines = $message -split '\r?\n'
if ($lines[0].Length -gt 50) { throw 'Subject exceeds 50 characters' }
if ($lines.Count -gt 1 -and $lines[1] -ne '') {
    throw 'Separate subject and body with a blank line'
}
for ($i = 1; $i -lt $lines.Count; $i++) {
    if ($lines[$i].Length -gt 70) {
        throw "Body line $($i + 1) exceeds 70 characters"
    }
}
```

After committing, validate the stored message from `git log -1 --format=%B`
against the same limits. Do not publish a commit that fails validation.

## Safe commit and publication procedure

1. Inspect the branch, status, staged diff, and relevant tests.
2. Stage only intended changes. Check for secrets and unrelated edits.
3. Preserve user changes; never discard them to make the worktree clean.
4. Use the user-approved author identity. If missing, ask rather than inventing
   an identity or changing global Git settings.
5. Validate the complete message, commit, and verify the stored message.
6. Publish only when authorized and report the actual remote outcome.

## Rewriting history

Do not amend, reset, or rewrite published history without explicit approval.
When asked to undo and recommit the latest commit:

1. Verify HEAD is the exact requested commit and inspect any pending changes.
2. Record the remote branch SHA before rewriting.
3. Use `git reset --soft HEAD^` to preserve the original changes in the index.
4. Stage approved additions and create a new, validated commit.
5. Verify the prior parent and intended tree contents are preserved.
6. Update the published branch with
   `git push --force-with-lease=<branch>:<recorded-sha> origin <branch>`.
7. If the lease fails, stop and inspect the new remote history; do not retry
   with an unconditional force push.

Never use a hard reset for commit-message corrections. Do not rewrite other
commits merely because they also violate the rules; ask for separate approval.
