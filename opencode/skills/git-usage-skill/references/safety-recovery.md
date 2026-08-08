# Git safety, conflicts, and recovery

## Risk classes

| Class | Examples | Default behavior |
|---|---|---|
| Read-only | `status`, `diff`, `log`, `show`, `branch -vv`, `remote -v`, `reflog show` | Safe to run, but repository config can invoke external helpers |
| Local mutation | `add`, `commit`, `switch`, `merge`, `stash`, `restore --staged` | Inspect first; verify afterward |
| Data loss | `restore` of worktree, `clean`, `reset --hard`, `worktree remove --force` | Preview/backup and get confirmation |
| History rewrite | amend, reset to an old commit, rebase, filter tools, moving tags | Private only unless explicitly coordinated |
| Shared mutation | `push`, remote/tag deletion, force-push | Show exact destination and policy |
| Object administration | `prune`, `gc --prune=now`, reflog expiry, repack | Never use casually during recovery |
| Code execution/configuration | hooks, filters, external diff/merge, `credential-store`, servers | Treat untrusted repositories and credentials carefully |

## Before destructive work

```bash
git rev-parse --show-toplevel
git status --short --branch
git diff
git diff --cached
git log --oneline --decorate --graph --all -20
git branch backup/before-destructive-operation
```

Do not silently stash or discard the user's work. If a backup branch is not suitable,
make a patch or a separate worktree. Explain that untracked content which was never
staged or committed is generally not recoverable by Git.

## Restore, reset, and revert

| Situation | Command | Result |
|---|---|---|
| Unstage a path, keep edits | `git restore --staged -- PATH` | index gets `HEAD` version |
| Discard unstaged path edits | `git restore --worktree -- PATH` | worktree gets index version |
| Restore both index/worktree | `git restore --source=HEAD --staged --worktree -- PATH` | discards local path changes |
| Move private tip, keep index/worktree | `git reset --soft REV` | ref moves only |
| Move private tip, unstage | `git reset REV` | ref and index move; files remain |
| Move private tip and overwrite files | `git reset --hard REV` | destructive; rescue first |
| Undo a shared commit | `git revert REV` | new inverse commit |

`git reset HEAD -- PATH` is an older unstage spelling. `git checkout -- PATH` is an
older dual-purpose spelling; prefer `restore` for clarity. `git reset --hard` can
overwrite tracked work and obstructing untracked paths, but it is not a substitute for
`git clean`, which removes untracked paths.

## Cleanup

Always preview:

```bash
git clean -nd -- PATH
git clean -ndx                 # includes ignored paths; inspect carefully
```

Only after confirming the preview:

```bash
git clean -fd -- PATH
git clean -fdx                 # very destructive; rarely appropriate
```

`.gitignore` only affects untracked paths. To stop tracking a local file while keeping
it on disk, use `git rm --cached -- PATH`; this does not remove old committed copies.
If a secret was committed, rotate/revoke it first and follow an approved
history-removal process. `git filter-repo` is a commonly recommended **external**
tool; it is not part of core Git. Rewriting all affected refs requires a backup,
coordination, and a carefully leased force-push/hosting cleanup.

## History rewrite and force-push

For a private topic:

```bash
git fetch origin main topic
expected=$(git rev-parse refs/remotes/origin/topic)
git branch backup/topic-before-rewrite HEAD
git log --oneline origin/main..topic
git rebase origin/main
git range-diff origin/main..backup/topic-before-rewrite origin/main..topic
```

If the rewritten topic is already remote, fetch the expected remote tip and use an
explicit lease where possible:

```bash
git push --dry-run --force-with-lease=refs/heads/topic:$expected \
  origin HEAD:refs/heads/topic
git push --force-with-lease=refs/heads/topic:$expected \
  origin HEAD:refs/heads/topic
```

If the lease fails, stop and inspect. Do not retry with `--force`. A plain
`--force-with-lease` is safer than `--force`, but an implicit lease can be affected
by background fetches. Never force-push shared integration, release, or protected
branches without explicit coordination.

## Conflict resolution

```bash
git status
git diff --name-only --diff-filter=U
git ls-files -u
git diff --cc
```

For an unmerged path, inspect the index stages:

```bash
git show :1:PATH       # common ancestor, if present
git show :2:PATH       # current side in the index
git show :3:PATH       # other side in the index
```

Resolve and validate:

```bash
# edit PATH; remove markers deliberately and run relevant tests
git diff --check -- PATH
git add -- PATH
git diff --cached --check
git diff --cached -- PATH
```

Then use only the matching `--continue`, `--skip`, or `--abort` command from
`decision-tree.md`. During a rebase, “ours” generally refers to the rebased base and
“theirs” to the commit being replayed, so inspect stages before using
`git restore --ours` or `--theirs`.

## Reflog recovery

Reflogs record local ref movement; they are not a remote backup and expire.

```bash
git reflog show HEAD --date=local
git log -g --oneline --decorate --all
git show 'HEAD@{1}'
git branch rescue/recovered-tip 'HEAD@{1}'
```

Create a rescue branch before resetting another ref. If the reflog no longer shows
the commit, inspect without pruning:

```bash
git fsck --full --no-reflogs --unreachable
git show OBJECT
git branch rescue/dangling OBJECT
```

Do not run `git gc`, `git prune`, aggressive repacking, or reflog expiry during
recovery. Objects may be made permanently unreachable. Recovery cannot restore an
untracked file that was never represented in the object database.

## Interrupted operations

The operation-specific `--abort` is preferred to manual reset because it knows the
sequencer state. `--quit` stops bookkeeping but leaves the index/worktree as-is; it is
not a rollback. After an abort, run `status`, inspect both diffs, and test.

## Trust boundary

Git can invoke repository-local hooks, clean/smudge filters, external diff/merge
drivers, credential helpers, and aliases. For an untrusted repository, inspect it in
a clean copy and avoid blindly running hooks or configured helpers. Do not use
`safe.directory=*` as a blanket workaround; verify ownership and allow only a known
path when necessary. `credential-store` can write plaintext credentials; prefer a
secure OS helper or SSH and never print secrets.
