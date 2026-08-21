# Git workflow patterns

These are adaptable patterns, not a universal branching policy. Replace `main`,
`origin`, `upstream`, `topic`, and placeholder paths with the project's actual names.
Run the read-only preflight from `decision-tree.md` before every pattern and verify
after every state-changing step.

## 1. New repository

Use when a directory has no repository yet. Add ignore and attribute policy before
tracking files; inspect for secrets, credentials, build output, and private config.

```bash
git init -b main
git status --short --untracked-files=all
# create or verify .gitignore and .gitattributes before tracking files
git check-ignore -v -- path/to/generated-file || true
git add -- .gitignore .gitattributes src/
git diff --cached --stat
git diff --cached --check
git diff --cached
git commit -m "Initial commit"
git log --oneline --decorate --graph -5
git remote add origin URL
git push -u origin main
```

Use `git add -p` or explicit paths when the directory contains unrelated material.
`git init --bare` is for a server-side repository, not a normal working directory.

## 2. Clone and orient

```bash
git clone URL project
git -C project status --short --branch
git -C project remote -v
git -C project branch -vv
git -C project log --oneline --decorate --graph --all -20
```

For submodules use `git clone --recurse-submodules URL`; for a large repository
consider `--filter=blob:none`, `--sparse`, or `--depth`, but record the tradeoff.
Shallow history can block merges, blame, bisect, and archaeology.

## 3. Daily feature branch

```bash
git fetch --prune origin
git switch -c topic --track origin/main
# edit files
git status --short --branch
git diff
git add -p -- path/to/file
git diff --cached
git diff --cached --check
git commit -m "Describe one coherent change"
git show --stat --oneline HEAD
git push -u origin topic
```

Keep commits coherent. If a branch already exists, use `git switch topic` only after
committing, stashing, or preserving current edits in a separate worktree.

## 4. Selective staging and partial commits

```bash
git status --short --untracked-files=all
git diff
git add -p -- path/to/file
git diff --cached -- path/to/file
git diff -- path/to/file
git commit -m "First focused change"
```

Repeat for the remaining hunks. `git add -N -- new-file` gives an intent-to-add entry
so a new file can be previewed with `git diff` before its content is staged. A file may
have both staged and unstaged edits; always inspect both diffs.

`git add -A` from the repository root stages tracked and untracked changes, including
deletions. `git add .` is path-scoped by the current directory. `git commit -a` stages
modified/deleted tracked files but not new files.

## 5. Inspect a change or prepare a PR

```bash
git status --short --branch
git status --short --untracked-files=all
git fetch upstream --prune
git log --oneline --decorate upstream/main..HEAD
git diff --stat upstream/main...HEAD
git diff --check upstream/main...HEAD
git diff upstream/main...HEAD
git log --reverse --format=fuller upstream/main..HEAD
git show --stat --oneline HEAD
```

Use triple-dot for “what this branch introduces since the merge base.” Use two
endpoints for a snapshot comparison. Review untracked files separately because diff
does not display them; for one untracked file, a temporary diff view is
`git diff --no-index -- /dev/null path/to/untracked` (it returns a difference status).
The PR comparison is not a substitute for the local staged/unstaged diffs. After
revising a published patch series, compare old and new:

```bash
git range-diff OLD_BASE..OLD_TIP NEW_BASE..HEAD
git push -u origin topic
```

Hosting-provider pull requests are outside core Git; Git supplies the branch, commits,
diff, and optional `request-pull` summary.

## 6. Sync without a blind pull

```bash
git status --short --branch
git fetch --prune origin
git branch -vv
git log --left-right --graph --oneline HEAD...origin/main
git diff --stat HEAD...origin/main
git diff --stat origin/main...HEAD
```

Then choose deliberately:

```bash
# integration branch that must only advance
git switch main
git merge --ff-only origin/main

# private topic branch that should be linear
git switch topic
git rebase origin/main

# preserve topology or integrate shared commits
git merge origin/main
```

`fetch` updates remote-tracking refs without changing the worktree. `pull` is fetch
plus an integration choice; if used, make it explicit with `--ff-only`, `--rebase`,
or the project's configured policy.

## 7. Review and integrate a topic

Choose the policy first:

| Need | Pattern |
|---|---|
| Linear private series | rebase topic on current base, then fast-forward/merge |
| Preserve shared topology | merge topic into integration branch |
| Explicit feature boundary | `merge --no-ff topic` |
| Integration branch cannot diverge | `merge --ff-only topic` |

Linear private series:

```bash
git switch topic
git fetch origin main topic
expected=$(git rev-parse refs/remotes/origin/topic)
git branch backup/topic-before-rebase HEAD
git rebase origin/main
# resolve conflicts, then: git add -- PATH && git rebase --continue
git range-diff origin/main..backup/topic-before-rebase origin/main..HEAD
git push --force-with-lease=refs/heads/topic:$expected \
  origin HEAD:refs/heads/topic
```

Shared integration:

```bash
git switch main
git fetch origin main
git merge --ff-only origin/main
git diff --stat main...topic
git diff --check main...topic
git merge --no-ff topic
# resolve conflicts, then: git add -- PATH && git merge --continue
git push origin main
```

Never rebase commits other developers may have based work on without coordination.

## 8. Merge conflict

```bash
git status
git diff --name-only --diff-filter=U
git ls-files -u
git diff --cc
```

Inspect stages for important paths, resolve deliberately, run tests, then:

```bash
git diff --check -- path/to/file
git add -- path/to/file
git diff --cached --check
git diff --cached -- path/to/file
git rebase --continue
```

If this is a merge instead, use `git merge --continue`; if it is a cherry-pick or
revert, use the matching sequencer command. If the integration should be abandoned,
use the matching `--abort`. `mergetool` can
help with a configured tool, but review the resulting file and staged diff. `rerere`
can reuse resolutions; enable it only when the team understands and reviews its
recorded results.

## 9. Cherry-pick or backport

First prove that the target branch does not already contain the change:

```bash
git fetch --prune origin
git log --cherry-pick --right-only --no-merges --oneline target...source
git show --stat --patch COMMIT
```

Then apply a reviewed fix:

```bash
git switch maintenance
git merge --ff-only origin/maintenance
git cherry-pick -x COMMIT
git show --stat --oneline HEAD
git diff HEAD^ --check
git push origin maintenance
```

`-x` records the source commit, useful for backports. For a merge commit, select a
mainline parent with `-m` only after inspecting the graph. Resolve with
`--continue`, abandon with `--abort`, or intentionally omit a patch with `--skip`.

## 10. Release and hotfix

Inspect the release base:

```bash
git fetch --prune origin
git switch main
git merge --ff-only origin/main
git log --first-parent --oneline --decorate -30
git describe --tags --always
git diff LAST_TAG...HEAD
```

Create a reviewed release tag:

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git show --stat vX.Y.Z
# If cryptographic signing is required, create with `git tag -s` instead, then:
# git tag -v vX.Y.Z
git push origin vX.Y.Z
```

Use `-s` for a cryptographically signed tag when the project has key policy. A
`Signed-off-by` trailer (`commit -s`) is not a cryptographic signature. Treat a
published release tag as immutable; correct a mistake with a new tag rather than
silently moving the old one.

For a hotfix, branch from the deployed tag, test and commit, merge into the production
branch, and propagate to supported branches with a reviewed merge or cherry-pick.

## 11. Undo local work

Inspect before choosing:

```bash
git status --short --branch
git diff
git diff --cached
git log --oneline --decorate -5
```

```bash
# keep worktree edits, remove from next commit
git restore --staged -- path/to/file

# discard only unstaged edits, after confirmation
git restore -- path/to/file

# fix the last private commit
git commit --amend

# move a private tip while keeping work
git reset --soft HEAD^

# undo a published commit additively
git revert COMMIT
```

Do not translate “undo” directly to `reset --hard`. Ask whether the user wants to
keep files, keep staging, move private history, or create a public inverse commit.

## 12. Stash and context switching

Prefer a small temporary commit or worktree for work that must survive. For a short
context switch:

```bash
git stash push -u -m "wip: describe context"
git switch other-branch
# work
git switch topic
git stash list
git stash show --stat stash@{0}
git stash apply --index stash@{0}
```

`apply` preserves the stash; `pop` attempts to apply and then drops it only if the
application succeeds. Conflicts still require inspection. Drop only after verifying
the restored work.

## 13. Recover a lost commit or branch

```bash
git status --short --branch
git reflog show HEAD --date=local
git show CANDIDATE
git branch rescue/recovered-tip CANDIDATE
git log --oneline --decorate rescue/recovered-tip
```

After verifying the rescue branch, deliberately choose whether to restore the original
branch with `git reset --hard rescue/recovered-tip` (only after confirming the
worktree is safe) or to cherry-pick selected commits. Only after the rescue ref exists
should another branch be moved. If reflogs no longer
contain the object, use `git fsck --full --no-reflogs --unreachable`, inspect dangling
commits, and create a rescue branch. Do not run prune/gc during this process.

## 14. Bisect a regression

Start with known-good and known-bad revisions and a deterministic test:

```bash
git status --short --branch
git bisect start
git bisect bad BAD_REV
git bisect good GOOD_REV
git bisect status
# test each checkout
git bisect good       # or: git bisect bad / git bisect skip
git bisect reset
```

For automation, `git bisect run ./test-script` must return a reliable classification
(0 good, 1–127 bad, 125 skip by convention). Save the result in a branch before
resetting if it matters. Shallow history may need deepening.

## 15. History archaeology

```bash
git log --all --oneline --decorate --graph
git log -S'important text' --oneline --all
git log -G'regex' --oneline --all
git log -L START,END:path/to/file
git blame -L START,END -- path/to/file
git show REV:path/to/file
git grep -n PATTERN REV -- path/to/file
```

Use `blame` as a pointer to commits, not as proof of intent. Follow the commit with
`show`, inspect renames with appropriate options, and remember that shallow clones
limit history searches.

## 16. Worktrees for parallel work

```bash
git worktree list
git worktree add -b topic ../project-topic origin/main
git -C ../project-topic status --short --branch
# work independently
git -C ../project-topic submodule update --init --recursive
git worktree remove ../project-topic
git worktree prune --dry-run
```

Worktrees share objects and most refs but have separate `HEAD`, index, and files. A
branch normally cannot be checked out in two worktrees. Use `remove`, not manual
directory deletion; preserve dirty work before `--force`.

## 17. Submodules

```bash
git submodule update --init --recursive
git submodule status --recursive
git diff --submodule=log
git -C path/to/submodule status --short
```

The superproject records a gitlink commit, not the submodule's files or current
branch. Work inside the submodule, commit and push there, then stage the pointer in
the superproject:

```bash
git -C path/to/submodule switch -c fix
git -C path/to/submodule status --short
git -C path/to/submodule add -- path/to/file
git -C path/to/submodule diff --cached
git -C path/to/submodule commit -m "Fix submodule"
git -C path/to/submodule push -u origin fix
git add -- path/to/submodule
git diff --cached --submodule=log
git commit -m "Update submodule"
git push --recurse-submodules=check origin HEAD:main
```

Inspect `.gitmodules` and synchronize changed URLs deliberately. Detached `HEAD` in a
submodule after `update` is expected until a contributor creates a branch.

## 18. Sparse, partial, and shallow repositories

```bash
git clone --depth=1 --single-branch URL
git rev-parse --is-shallow-repository

git clone --filter=blob:none --sparse URL
git sparse-checkout set --cone src docs
```

Shallow clone limits ancestry; partial clone defers object contents; sparse checkout
limits files in the worktree. They are different controls. Use full/deepened history
for release work, complex merges, blame, pickaxe searches, and bisect.

## 19. Patch and email workflow

For a patch series:

```bash
git format-patch --cover-letter --output-directory out BASE..HEAD
git apply --check out/0001-change.patch
git am --3way out/0001-change.patch
```

Inspect the generated patch before sending. `git apply --check PATCH` is a dry-run;
`git am` records author/commit metadata and has `--continue`, `--skip`, and `--abort`.
`send-email`, `imap-send`, and SMTP configuration have real external side effects;
use their dry-run/help modes and redact credentials. `request-pull` summarizes a
branch; it does not submit a hosting-provider pull request.

## 20. Offline transfer and archives

```bash
git bundle create repo.bundle --all
git bundle verify repo.bundle
git bundle list-heads repo.bundle
git clone repo.bundle new-repo
git archive --format=tar --prefix=project/ REV | gzip > project.tar.gz
```

Bundles carry refs/objects for offline transfer; archives carry a tree snapshot and
do not preserve repository history. Verify provenance and the intended revision.

## 21. Maintenance and diagnostics

```bash
git count-objects -vH
git fsck --full
git commit-graph verify
git multi-pack-index verify
git maintenance run --auto
```

Prefer scheduled maintenance for normal optimization, but defer all maintenance and
object cleanup while recovering until rescue refs are verified. Do not run `gc --prune=now`,
`prune`, or reflog expiry while recovering history. `fsck` diagnoses reachability and
integrity; it is not a general repair command. `diagnose` and `bugreport` may include
paths/configuration, so inspect generated files before sharing.

## 22. Fork and upstream workflow

```bash
git remote add upstream CANONICAL_URL
git fetch upstream --prune
git switch main
git merge --ff-only upstream/main
git push origin main
git switch -c topic --track origin/main
```

Keep `origin` (your fork/publish remote) distinct from `upstream` (canonical source).
Fetch before comparing; remote-tracking refs are local cached bookmarks.
