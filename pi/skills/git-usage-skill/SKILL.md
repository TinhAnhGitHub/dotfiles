---
name: git-usage-skill
description: >-
  Comprehensive Git CLI and repository-workflow guidance. Use this skill for any Git
  command or repository task, including init, clone, status, add, commit, diff, log,
  revisions, branches, switch, checkout, merge, rebase, cherry-pick, revert, reset,
  restore, stash, remotes, fetch, pull, push, tags, worktrees, submodules, patches,
  email, hooks, ignore rules, attributes, credentials, signing, bisect, blame, reflog,
  recovery, plumbing, internals, maintenance, or server administration. Trigger it
  even when the request is phrased indirectly as undoing changes, inspecting a PR,
  resolving a conflict, recovering a lost commit, or understanding a Git error.
  Establish the installed Git version and repository state, select the safest workflow,
  and consult the relevant official reference before giving version-sensitive flags.
compatibility: Git CLI; verify the installed version because commands and options vary by version.
metadata:
  sources: git-scm.com/docs and Pro Git 2nd edition
  research_date: 2026-08-08
  skill_version: "1.0"
---

# Git usage

Use this skill as a decision aid, not as permission to mutate a repository. Prefer
inspection first, explain the expected state after each mutation, and leave a clear
abort or recovery path. The bundled references contain the comprehensive command
catalog, workflow patterns, safety rules, official guide map, and Pro Git coverage.

## 1. Mandatory preflight

Before recommending a state-changing command, establish enough context to avoid
acting on the wrong repository or the wrong history:

```bash
git --version
git rev-parse --show-toplevel
git status --short --branch
git branch -vv
git remote -v
git worktree list
```

If the command is for a script, use machine-safe output such as
`git status --porcelain=v1 -z`; never parse human-oriented status text. If the path is
not a repository, explain whether the user wants `git init` or `git clone`. If Git is
older than the requested syntax, use `git help <command>` and the matching manual
page for the installed version rather than silently substituting flags.

Do not run a destructive command against a user repository merely to diagnose it.
Ask for approval before discarding work, rewriting history, deleting refs or files,
changing remotes, changing credentials, or running hooks/server commands.

## 2. The state model to keep visible

Reason in terms of three trees and refs:

| State | Meaning | Inspect with |
|---|---|---|
| `HEAD` and refs | Current commit and branch pointers | `git log -1 --decorate`, `git show-ref` |
| Index | Proposed contents of the next commit | `git diff --cached`, `git ls-files --stage` |
| Worktree | Files currently on disk | `git diff`, `git status` |

Use this inspection compass:

```bash
git status --short --branch             # state, branch, ahead/behind
git diff                                # worktree versus index
git diff --cached                       # index versus HEAD
git diff HEAD                           # index + worktree versus HEAD
git diff --stat HEAD~1 HEAD             # two committed snapshots
git diff BASE...HEAD                    # merge-base(BASE, HEAD) versus HEAD
git log --oneline --decorate --graph --all
git show --stat --oneline REV
```

`git diff` does not show untracked files. `git diff A B` and `git diff A..B` compare
the endpoint trees; `git diff A...B` compares `B` with the merge base of `A` and `B`.
For `git log`, `A..B` means commits reachable from `B` but not `A`. Use `--` to end
revision/options and begin paths, and quote pathspec globs.

## 3. Route by intent

Read only the relevant reference before answering. Use `references/workflows.md` for
the complete command sequences and `references/decision-tree.md` for quick routing.

| User intent | Read |
|---|---|
| “What changed?”, staged vs unstaged, PR review | `references/decision-tree.md`, `references/workflows.md` |
| initialize, clone, daily stage/commit/push | `references/workflows.md` |
| branch, sync, merge, rebase, cherry-pick | `references/workflows.md`, `references/safety-recovery.md` |
| conflict, abort, continue, “ours/theirs” | `references/safety-recovery.md` |
| undo, reset, restore, revert, stash, lost commit | `references/safety-recovery.md` |
| release, tags, signing, backport, hotfix | `references/workflows.md`, `references/command-catalog.md` |
| worktrees, submodules, sparse/partial/shallow clone | `references/workflows.md`, `references/command-catalog.md` |
| bisect, blame, grep, history archaeology | `references/workflows.md`, `references/command-catalog.md` |
| hooks, ignore, attributes, credentials, config | `references/guides-and-book.md`, `references/command-catalog.md` |
| plumbing, objects, refs, packfiles, server administration | `references/command-catalog.md`, `references/guides-and-book.md` |
| “What does this command/flag do?” | `references/command-catalog.md`, then `git <command> -h` |
| book concept or section | `references/guides-and-book.md` |

## 4. Published-history rule

Classify commits as **private/unpublished** or **shared/published** before choosing
an undo or integration operation:

- Private history may be rewritten with interactive rebase, amend, or reset after a
  backup ref and a review of the affected range.
- Shared history should be changed additively with `git revert`, or integrated with
  a merge according to the project policy.
- A rebased private branch that already has a remote copy may require
  `git push --force-with-lease`, never an unexamined `--force`.
- Never force-update a protected or shared integration branch without explicit team
  coordination.

Before rewriting, create an anchor and inspect it:

```bash
git branch backup/before-history-change
git log --oneline --decorate BASE..HEAD
```

## 5. Safety defaults

Treat these as confirmation points, not casual suggestions:

| Risk | Safer first step |
|---|---|
| discard worktree edits | `git diff`; then explain `git restore` and its loss |
| unstage | `git restore --staged -- PATH` (keeps worktree edits) |
| move local history | backup branch, then `reset` or `rebase` |
| undo a published commit | `git revert REV` |
| remove untracked files | `git clean -nd`; only then consider `-fd` |
| include ignored files in cleanup | preview `git clean -ndx`; explain the risk |
| force-push a rewritten topic | fetch and use an explicit `--force-with-lease` |
| recover a lost commit | inspect `git reflog`; create a rescue branch before moving refs |
| repair/compact objects | defer all maintenance/prune/gc until recovery is complete |
| untrusted repository | do not trust local hooks, filters, diff drivers, or config |

`git reset --hard`, `git restore` that overwrites files, `git clean`, `branch -D`,
reflog expiry/deletion, `prune`, `gc --prune=now`, `filter-branch`, and remote/tag
deletion need an explicit warning and a recovery/backup discussion.

## 6. Conflict protocol

When `status` reports an in-progress merge, rebase, cherry-pick, or revert, do not
start another integration operation. Inspect and use the matching control flow:

```bash
git status
git diff --name-only --diff-filter=U
git ls-files -u
git diff --cc
# edit and test files, then:
git add -- PATH
git diff --cached --check
git merge --continue       # or rebase/cherry-pick/revert --continue
```

Use the matching `--abort` when abandoning the operation. Explain that “ours” and
“theirs” can have reversed practical meanings during a rebase; inspect index stages
`:1:PATH`, `:2:PATH`, and `:3:PATH` before selecting a side.

## 7. Response contract

For a practical Git answer, provide:

1. Assumptions: repository, branch, remote, shell, Git version, and whether commits
   are shared.
2. Read-only inspection commands first.
3. The smallest safe command sequence, with `--` before paths.
4. Expected state after each meaningful step.
5. Verification: status, relevant diff/log, tests, and push destination.
6. Abort/recovery instructions and a warning for any irreversible or shared-history
   operation.
7. Official source links for unusual or version-sensitive behavior.

Do not conflate core Git with hosting-provider APIs, Git LFS, IDE actions, or GUI
behavior. Say when a workflow depends on GitHub/GitLab/server policy. For exact
syntax, use:

```bash
git help -a
git help -g
git <command> -h
git help <command>
```

Then consult the current manual at `https://git-scm.com/docs/git-<command>`.
For the separately installed Scalar executable, use `scalar -h` and
`https://git-scm.com/docs/scalar` instead of assuming it is a `git scalar` subcommand.

## 8. References and source scope

- Command taxonomy and concise usage: `references/command-catalog.md`.
- Workflow recipes, especially diff/status/log inspection: `references/workflows.md`.
- Destructive operations, conflicts, and recovery: `references/safety-recovery.md`.
- Official guides and the complete Pro Git section/subsection map: `references/guides-and-book.md`.
- Research versions, coverage boundaries, and source links: `references/source-ledger.md`.

The reference set is an original, condensed guide; it does not reproduce the Pro Git
book. The book is linked for concepts and attribution, while current Git manuals and
the locally installed `git -h` output control exact behavior.
