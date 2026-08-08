# Git decision tree and inspection matrix

## Start here

1. **Which repository?** Run `git rev-parse --show-toplevel` and
   `git worktree list`.
2. **Which state?** Run `git status --short --branch`; note untracked, staged,
   unstaged, detached-HEAD, and any in-progress operation.
3. **Which history?** Run `git branch -vv`, `git remote -v`, and
   `git log --oneline --decorate --graph --all -20`.
4. **Which intent?** Choose inspect, prepare a commit, integrate, publish, recover,
   debug, or administer. Do not skip the published/private history question.

## Inspection compass

| Question | Command | Important boundary |
|---|---|---|
| What is dirty? | `git status --short --branch` | Does not show the content of untracked files |
| What is unstaged? | `git diff` | Worktree versus index; tracked paths only |
| What is staged? | `git diff --cached` | Index versus `HEAD`; this is the next commit |
| What would commit include? | `git diff HEAD` | Index plus worktree versus `HEAD` |
| What are untracked files? | `git status --short --untracked-files=all` | Check secrets and generated files |
| Why is a path ignored? | `git check-ignore -v -- PATH` | `.gitignore` does not untrack files |
| What did one commit do? | `git show --stat --patch REV` | `REV` can be a tag, ref, or revision expression |
| What is a file at a revision? | `git show REV:path/to/file` | Use `--` for path arguments to other commands |
| What changed since the base? | `git diff BASE...HEAD` | Merge-base to `HEAD`, ideal for PR review |
| Which commits are only on topic? | `git log BASE..topic` | Reachability query, not a patch comparison |
| How did two patch series change? | `git range-diff OLD...NEW` | Compare corresponding commits after rebase |
| Which branches contain it? | `git branch --contains REV` | Fetch first if remote state matters |
| What is the remote really advertising? | `git ls-remote --heads origin` | Network read; remote-tracking refs are cached |
| Where did a ref point before? | `git reflog show REF` | Local recovery log, not a remote backup |

## Diff and range rules

| Form | Meaning |
|---|---|
| `git diff` | worktree vs index |
| `git diff --cached` / `--staged` | index vs `HEAD` |
| `git diff HEAD` | worktree + index vs `HEAD` |
| `git diff A B` or `A..B` | endpoint tree `A` vs endpoint tree `B` |
| `git diff A...B` | merge-base of `A`/`B` vs `B` |
| `git log A..B` | commits reachable from `B`, not `A` |
| `git log A...B` | symmetric difference of reachable commits |
| `git log --left-right A...B` | label which side owns each commit |

For a PR, fetch the target branch, then use `git diff --stat target...HEAD`,
`git diff --check target...HEAD`, and `git diff target...HEAD`. For an ordinary
two-snapshot comparison, use `git diff A B`; do not replace it with a triple-dot
range by habit.

## Select the mutation

| Goal | Prefer | Do not confuse with |
|---|---|---|
| Stage content | `git add`, `git add -p` | `commit -a` does not add new files |
| Unstage but keep edits | `git restore --staged -- PATH` | `restore --worktree` discards edits |
| Discard local file edits | `git restore -- PATH` after review | `reset` may also move refs |
| Move private branch tip | `git reset` or rebase with backup | never for shared history without coordination |
| Undo a published commit | `git revert REV` | reset changes the branch pointer |
| Combine histories | `git merge` | rebase recreates commit IDs |
| Replay selected changes | `git cherry-pick REV` | it creates a new commit |
| Temporarily park work | `git stash push -u -m "reason"` | a stash is not a durable collaboration branch |

## Remote update choice

```text
fetch -> inspect log/diff -> choose ff-only merge, merge, or rebase -> verify -> push
```

- Use `fetch` when the user wants remote data without changing the worktree.
- Use `merge --ff-only` when an integration branch must only advance.
- Use `rebase` for private topic commits when a linear series is desired.
- Use `merge` when preserving topology or integrating shared commits matters.
- Use explicit `pull --ff-only` or `pull --rebase` only when the policy is known;
  avoid a blind default `pull`.

## In-progress operation routing

`git status` is authoritative. Route to exactly one control family:

| State | Continue | Skip | Abort |
|---|---|---|---|
| merge | `git merge --continue` | — | `git merge --abort` |
| rebase | `git rebase --continue` | `git rebase --skip` | `git rebase --abort` |
| cherry-pick | `git cherry-pick --continue` | `--skip` | `--abort` |
| revert | `git revert --continue` | `--skip` | `--abort` |
| `am` mailbox apply | `git am --continue` | `git am --skip` | `git am --abort` |
| bisect | classify `good`/`bad`/`skip` | `git bisect skip` | `git bisect reset` |

Resolve, test, stage, and review the staged diff before continuing. Never tell a
user to run a second merge/rebase while one of these states is active.
