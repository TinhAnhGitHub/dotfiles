# Git command catalog

This catalog follows the categories in the official `git(1)` reference. Each entry
gives the normal role, a useful invocation shape, and the boundary that prevents a
common mistake. It is intentionally concise: run `git COMMAND -h` for the installed
release, then read `https://git-scm.com/docs/git-COMMAND` for full option semantics.

## Contents

- [Discovery and setup](#discovery-and-setup)
- [Project and snapshot porcelain](#project-and-snapshot-porcelain)
- [Branch, integration, and sharing porcelain](#branch-integration-and-sharing-porcelain)
- [Inspection and debugging porcelain](#inspection-and-debugging-porcelain)
- [Patching, email, and external systems](#patching-email-and-external-systems)
- [Administration and recovery](#administration-and-recovery)
- [Plumbing: object, index, ref, and pack operations](#plumbing-object-index-ref-and-pack-operations)
- [Plumbing: interrogation and transport](#plumbing-interrogation-and-transport)
- [Helpers, aliases, and extensions](#helpers-aliases-and-extensions)
- [Version gates](#version-gates)

## Discovery and setup

### `git`

Top-level command dispatcher and conventions. Use `git --version`, `git -h`,
`git help -a`, `git help -g`, and `git <command> -h` to discover the installed CLI.
Do not infer availability from a newer online manual.

### `git config`

Read/write system, global, local, worktree, and command-scoped configuration.
Inspect origins and scopes with `git config --list --show-origin --show-scope`; set
identity with `git config --global user.name "Name"` and `user.email`. Treat aliases,
hooks paths, filters, external tools, credential helpers, and URL rewrites as code or
security-sensitive configuration.

### `git help`

Open command, guide, glossary, or configuration help. Use `git help <command>` for
the installed manual and `git help -a`/`-g` for discovery. It is safer and more exact
than guessing flags from memory.

### `git version`

Report the executable version/build options. Include it in bug reports and in answers
that use newer commands.

### `git bugreport` and `git diagnose`

Collect diagnostic files for Git support. Inspect the output for paths and
configuration before sharing; these commands do not repair a repository.

## Project and snapshot porcelain

### `git init`

Create or reinitialize a repository: `git init -b main`. Reinitializing preserves
objects, but `--bare` creates a server-style repository with no worktree.

### `git clone`

Copy a repository and configure `origin`: `git clone URL DIR`. Use `--recurse-submodules`
for submodules, `--depth` for deliberately shallow clones, `--filter=blob:none` for
partial clones, and `--sparse` for a limited worktree. Record the limitations before
using shallow/partial history for archaeology or release work.

### `git status`

Show worktree/index state: `git status --short --branch`; use
`--porcelain=v1 -z` for scripts. It distinguishes staged, unstaged, deleted, and
untracked paths. It does not show untracked file contents; refresh/index-lock behavior
matters in concurrent scripts.

### `git add`

Copy worktree content into the index: `git add -- PATH`, `git add -p`, `git add -u`,
or `git add -A`. Review `git diff --cached` afterward. `-A` can stage secrets or
unrelated changes; `-p` is the default for focused commits. `-N` marks a new path for
diff inspection without staging its contents.

### `git diff`

Compare worktree/index/trees: `git diff`, `git diff --cached`, `git diff HEAD`,
`git diff BASE...HEAD`. Useful review options include `--stat`, `--name-status`,
`--check`, `--word-diff`, and rename detection. It does not include untracked files.
Triple-dot is merge-base-to-right-tip; two endpoints compare snapshots.

### `git commit`

Record the index: `git commit -m "message"`. `-a` includes modified/deleted tracked
files but not new files; `--amend`, interactive fixups, and `--no-verify` have policy
and history consequences. Review the staged diff and commit message before signing or
publishing.

### `git restore`

Restore worktree and/or index paths: `git restore --staged -- PATH` unstages while
keeping edits; `git restore -- PATH` discards unstaged edits. Use `--source`,
`--worktree`, and `--staged` deliberately. It can destroy uncommitted data.

### `git reset`

Move refs and/or index/worktree. `--soft` keeps index/worktree, mixed (default) resets
the index, and `--hard` overwrites files. `git reset HEAD -- PATH` only unstages a
path. Use for private history or index operations, not as a public undo mechanism.

### `git revert`

Create a new commit that inverses an existing commit: `git revert REV`. Use for
published history. Reverting a merge needs `-m PARENT`; inspect the graph first.

### `git rm`

Remove tracked paths from worktree and index. `git rm --cached -- PATH` stops tracking
while preserving the file. Use `-r` for directories and review before `-f`.

### `git mv`

Move/rename tracked paths: `git mv OLD NEW`. Git detects renames from content; verify
with `git diff --cached --name-status`.

### `git clean`

Remove untracked paths. Always preview with `git clean -nd`; `-d` includes directories
and `-x` includes ignored files. This is destructive and has no normal Git undo.

### `git notes`

Attach notes under a separate `refs/notes/*` namespace: `git notes add REV` and
`git notes show REV`. Notes need explicit fetch/push configuration and are not commit
message edits.

## Branch, integration, and sharing porcelain

### `git branch`

List/create/delete/rename branches: `git branch -vv`, `git branch -c NAME`,
`git branch -d NAME`, `git branch --merged`. `-D` force-deletes unmerged work; inspect
and back up first. `-u` sets upstream tracking.

### `git switch`

Switch branches: `git switch topic`, create with `-c`, track with
`--track origin/main`, and detach with `--detach REV`. It avoids the dual meaning of
old `checkout`; `--discard-changes` is destructive.

### `git checkout`

Legacy dual-purpose branch switch and path restore. Prefer `switch` for branches and
`restore` for paths; retain `checkout -b`/`--orphan` only when compatibility or a
specific detached/orphan workflow requires it.

### `git merge`

Join histories. Use `--ff-only` for a no-surprise fast-forward, `--no-ff` for an
explicit feature boundary, and `--abort`/`--continue` for conflicts. `--no-commit`
does not stop a fast-forward unless paired with `--no-ff`.

### `git rebase`

Replay commits onto a new base: `git rebase origin/main`; use `-i` for private-series
cleanup, `--onto` for transplanting, and `--autosquash` for fixups. It changes commit
IDs. Use a backup and never rewrite shared history casually. Resolve with
`--continue`, skip only knowingly with `--skip`, or abandon with `--abort`.

### `git cherry-pick`

Apply the change from selected commits as new commits: `git cherry-pick REV`, `-x` for
backport provenance, `-n` to stage without committing. A merge commit needs `-m`; use
the sequencer's continue/skip/abort controls during conflicts.

### `git stash`

Save dirty work temporarily: `git stash push -u -m "reason"`; inspect with `list` and
`show`; prefer `apply` when preserving the stash matters. `pop` may conflict and
`drop` is destructive. A branch/worktree or temporary commit is more durable.

### `git tag`

List/create/verify release references. Prefer annotated `git tag -a`; use signed
`git tag -s` when cryptographic verification is required, then verify that signed tag
with `git tag -v`. An unsigned annotated tag is inspected with `git show`, not
`tag -v`. Avoid moving/deleting published tags; push tags explicitly instead of
blindly using `--tags`.

### `git fetch`

Download objects and update remote-tracking refs without integrating: `git fetch
--prune origin`. Fetch before trusting `origin/main` or ahead/behind output.

### `git pull`

Fetch then integrate. Make the policy explicit with `--ff-only`, `--rebase`, or a
deliberate merge; a blind pull can create an unwanted merge or rewrite local commits.

### `git push`

Publish refs: `git push -u origin topic`, `--dry-run` to preview, `--delete` to remove
a remote branch, and `--force-with-lease` for a coordinated private rewrite. Plain
`--force` can overwrite collaborators and broad refspecs.

### `git remote`

Manage remote names/URLs and tracking: `git remote -v`, `show`, `get-url --all`,
`set-url`, `add`, `rename`, `remove`, and `prune`. A remote-tracking branch is a local
cached ref, not a live server query.

### `git worktree`

Create multiple worktrees from one object database: `git worktree add -b topic DIR
START`. List, lock, move, remove, repair, and prune with their subcommands. Do not
manually delete a dirty worktree; use `remove` and protect unsaved work.

### `git submodule`

Manage nested repositories recorded as gitlinks: `update --init --recursive`, `status`,
`sync`, `foreach`, and `add`. Commit/push inside the submodule, then commit the
superproject pointer. Use `push --recurse-submodules=check` before publishing.

### `git sparse-checkout`

Limit the worktree, commonly `git sparse-checkout set --cone src docs` followed by
`add` as needed. Older releases may require an explicit `init`; check local help.
It changes checked-out paths, not history; combine with partial clone for large
repositories and verify patterns before editing.

### `git archive`

Export a tree snapshot as tar/zip: `git archive --prefix=project/ REV`. It does not
contain Git history. Remote archive requires server support.

### `git bundle`

Package refs/objects for offline transfer: `git bundle create FILE --all`, then
`verify`, `list-heads`, `unbundle`, or clone from it. Check that the bundle contains
the required base before transfer.

### `git maintenance` and `git gc`

Use `git maintenance register/start/run` for scheduled optimization and `git gc`
for ordinary cleanup when no recovery is in progress. `register`/`start` change
configuration or schedulers, and `gc --prune=now` may delete unreachable objects;
defer all maintenance while trying to recover history.

### `git backfill` and `git history`

These newer online-reference commands are version-gated/experimental. `git backfill`
can fetch missing blobs in a partial clone for a selected revision range; verify the
network/object policy first. `git history` provides higher-level history rewriting
operations in releases that ship it; it can rewrite refs and is not a replacement
for understanding interactive rebase. Run the installed `git <command> -h` and read
the matching manual before using either command.

### Newer low-level and large-repository commands

- **`git refs`** — list/verify/optimize refs or migrate a ref storage backend. Treat
  migration as an administrative change and test on a copy first.
- **`git replay`** — experimental commit replay/ref-action plumbing for controlled
  server or CI workflows; inspect its printed ref actions before applying anything.
- **`git repo`** — experimental repository metadata/structure reporting; use it for
  diagnostics, not as a replacement for `rev-parse` in portable scripts.
- **`git diff-pairs`** — experimental stdin-oriented blob-pair diff plumbing; use only
  when implementing a deliberate diff pipeline.
- **`git format-rev`** — experimental streaming revision formatting; verify input
  mode and NUL behavior before scripting.
- **`git last-modified`** — experimental per-path last-commit reporting; use `log` or
  `blame` when compatibility matters.
- **`git url-parse`** — parse Git URL components for scripts; never log passwords or
  credential-bearing URLs.
- **`scalar`** — large-repository enlistment/maintenance tool when distributed by
  the installed Git; it configures clone, sparse, and maintenance behavior, so inspect
  its plan before applying it to an existing checkout.

### `git range-diff`

Compare two versions of a patch series after a rebase: `git range-diff OLD_RANGE NEW_RANGE`.
It reviews commit correspondence, not just endpoint trees.

### `git describe`

Give a commit a tag-relative name for builds: `git describe --tags --always REV`. It
depends on available tags and is not a cryptographic release verification.

## Inspection and debugging porcelain

### `git log`

Walk history. Useful forms include `--oneline --decorate --graph --all`, `-p`,
`--stat`, `--first-parent`, `--follow -- PATH`, `-SSTRING`, `-GREGEX`, `--author`,
`--grep`, `--since`, `--ancestry-path`, `--left-right`, and `--cherry-pick`. Quote
revision/path arguments and remember `A..B` is a reachability range.

### `git show`

Inspect a commit, tag, tree, or blob: `git show --stat --patch REV` or
`git show REV:path`. Use `--show-signature` for signed commit/tag inspection.

### `git shortlog`

Summarize log entries by author, often `git shortlog -sne REV_RANGE` for release or
contribution reports. It is read-only.

### `git grep`

Search tracked content in a worktree or revision: `git grep -n PATTERN REV -- PATH`.
It is not a general search of untracked files; use shell tools separately when needed.

### `git blame` and `git annotate`

Attribute lines to the last modifying commit: `git blame -L START,END -- PATH`.
Follow the commit with `show`; use `-w`, `-M`, `-C`, or ignored revisions when
whitespace/renames would mislead. `annotate` is a legacy synonym.

### `git bisect`

Binary-search a regression with `start`, `good`, `bad`, `skip`, `run`, `log`, and
`reset`. Begin with a clean/safely saved worktree and deterministic test; finish with
`git bisect reset`.

### `git difftool`

Open configured external diff tools, optionally directory comparisons. It is a view
layer over diff; external tools and text conversions are executable configuration, so
do not trust them in an untrusted repository.

### `git merge-tree`

Compute a merge without touching the index/worktree. Use it as a dry-run/CI check and
read its version-specific output before scripting around it.

### `git rerere`

Record and reuse conflict resolutions when `rerere.enabled` is configured. Inspect
`status`/`diff` and test every reused resolution; stale recorded resolutions can be
wrong.

### `git show-branch` and `git whatchanged`

Legacy branch/diff views. Prefer `git log --graph --decorate --all` and `git log -p`
for new workflows.

### `git verify-commit` and `git verify-tag`

Check cryptographic signatures with the configured GPG/SSH verification support. A
successful check proves signature validity, not the trust policy for the signer.

## Patching, email, and external systems

### `git apply`

Apply a patch to worktree/index. Start with `git apply --check PATCH`; use
`--cached`, `--index`, `--3way`, or `--reverse` only when the patch/base assumptions
are known. It does not by itself create a commit.

### `git format-patch`

Create mailbox patch series from commits: `git format-patch --stdout BASE..HEAD` or
an output directory. Review patches, cover letters, trailers, and range-diff before
sending.

### `git am`

Apply mailbox patches as commits, optionally `--3way`; continue/skip/abort a stopped
series. Inspect author and signoff metadata before committing to an integration branch.

### `git send-email`, `git imap-send`, and `git request-pull`

Email-based contribution tools. `send-email` sends mail, `imap-send` uploads mail,
and `request-pull` summarizes pending work. Use dry-run/help options, verify
recipients, and protect SMTP/IMAP credentials; these are not hosting-provider APIs.

### `git svn`, `git p4`, and CVS/Arch/quilt bridges

Interop commands: `svn` for Subversion, `p4` for Perforce, `cvsimport`/
`cvsexportcommit`/`cvsserver` for CVS, `archimport` for GNU Arch, and `quiltimport`
for quilt patches. Read the bridge manual and test on a disposable clone; operations
such as `dcommit`/`submit` write to an external system.

### `git fast-export` and `git fast-import`

Export a repository as a fast-import stream or import one produced by a migration/tool.
Use `git fast-export --all` for a controlled migration input and `git fast-import` only
in a disposable or explicitly managed destination; import streams can create or move
refs and should be validated before publication.

## Administration and recovery

### `git reflog`

Show ref movement, especially `git reflog show HEAD` and `git log -g`. It is local,
expires, and must not be treated as a backup. Do not expire/delete it during recovery.

### `git fsck`

Verify connectivity/integrity and find unreachable objects: `git fsck --full` or
`--no-reflogs --unreachable`. It diagnoses; it does not magically repair all damage.

### `git count-objects`, `git repack`, `git pack-refs`, `git prune`, and `git prune-packed`

Inspect size with `count-objects -vH`; packing commands optimize storage. `prune` can
delete unreachable objects and `prune-packed` removes loose duplicates. Prefer normal
maintenance and dry-run/backup discipline.

### `git filter-branch`

Legacy history-rewrite tool with documented pitfalls. Do not recommend it casually;
use an approved modern history-rewrite tool/process, backup, secret rotation, and
coordination. Any rewrite changes commit IDs and requires updating all affected refs.

### `git replace`

Temporarily substitute an object via replacement refs for experiments or grafted
history. It changes what many commands see; inspect/delete replacement refs and use
`--no-replace-objects` when comparing normal history.

### `git instaweb` and `gitweb`

Run/view a local gitweb interface. Treat server configuration, exposed paths, and
access control as security-sensitive; these are not required for normal CLI work.

## Plumbing: object, index, ref, and pack operations

Plumbing is useful for scripts, diagnostics, and understanding Git internals. Prefer
porcelain for normal work. Validate inputs, use `--`/NUL-safe modes where applicable,
and never mutate refs or the index without a backup and an atomicity plan.

### Object and tree commands

- **`git cat-file`** — inspect object type/size/content (`-t`, `-s`, `-p`, `-e`,
  `--batch`). The universal read-only object inspector; lazy fetching can have side
  effects in partial clones.
- **`git hash-object`** — hash content and optionally write an object (`-w`). Written
  but unreachable objects are candidates for garbage collection.
- **`git ls-tree`** — list a tree at a revision (`-r --name-only REV`).
- **`git write-tree`** — write a tree from the index; fails for unmerged entries.
- **`git read-tree`** — load trees into the index, optionally update the worktree;
  it can overwrite index state and is mostly plumbing.
- **`git commit-tree`** — create a commit object from a tree/parents; it does not move
  a branch ref, so pair it with carefully reviewed ref updates.
- **`git mktree`** and **`git mktag`** — construct validated tree/tag objects from
  formatted input; use only for tooling or experiments.
- **`git checkout-index`** — materialize index entries into the worktree; `-f` can
  overwrite files.
- **`git unpack-file`** — write a blob to a temporary file for scripts.
- **`git merge-file`** — perform a three-way file merge, usually for tooling; it can
  write the target file, so use a copy or `-p` when a non-mutating result is needed.
- **`git merge-index`** and **`git merge-one-file`** — low-level helpers that invoke
  per-path merge logic; use the porcelain conflict workflow instead of calling them
  directly unless implementing Git tooling.

### Index and ref commands

- **`git ls-files`** — inspect index/worktree entries (`--stage`, `--unmerged`,
  `--others`, `-z`); a key diagnostic for staging and conflicts.
- **`git update-index`** — low-level index flags/content (`--add`, `--remove`,
  `--cacheinfo`, `--skip-worktree`, `--assume-unchanged`). The latter flags can make
  normal changes disappear from status; do not use them casually.
- **`git update-ref`** — atomically create/move/delete refs, optionally with an old
  value guard. Prefer it over writing ref files directly.
- **`git symbolic-ref`** — inspect/change symbolic refs such as `HEAD`; changing them
  bypasses normal porcelain checks.
- **`git show-ref`** — list/verify local refs; use `for-each-ref` for formatting.
- **`git rev-parse`** — validate revisions, find repository paths, resolve upstreams,
  and parse script arguments (`--verify`, `--show-toplevel`, `--git-dir`). Quote
  user-supplied revisions and validate expected object types.

### Pack and graph commands

- **`git pack-objects`**, **`index-pack`**, and **`unpack-objects`** — transport and
  pack construction primitives; normally used by fetch/push rather than by hand.
- **`git commit-graph`** — write/verify commit-graph performance data.
- **`git multi-pack-index`** — verify/write/repack/expire multi-pack indexes in large
  repositories; `repack`/`expire` can remove objects, so use maintenance policy.
- **`git verify-pack`** and **`git show-index`** — inspect/verify pack indexes.
- **`git pack-redundant`** — report redundant packs; prefer modern maintenance.
- **`git patch-id`** — compute a patch identity for detecting equivalent changes
  across rebases/cherry-picks.

## Plumbing: interrogation and transport

### Revision and ref interrogation

- **`git rev-list`** — enumerate commits/objects for scripts and traversal; it powers
  much of log, bisect, and transport.
- **`git for-each-ref`** — format/sort/filter refs; use `--format` and NUL/shell-safe
  formats when feeding scripts.
- **`git for-each-repo`** — run a command across repositories listed by configuration;
  verify the list before executing mutations.
- **`git ls-remote`** — query advertised remote refs without cloning; it is a network
  read and does not update local remote-tracking refs.
- **`git merge-base`** — find common ancestors or test ancestry (`--is-ancestor`);
  useful for scripts and PR base calculations.
- **`git cherry`** — report commits not yet applied upstream, accounting for patch
  equivalence; inspect with `-v`.
- **`git name-rev`** — assign symbolic names to object IDs for reports.
- **`git diff-files`**, **`git diff-index`**, and **`git diff-tree`** — plumbing forms
  of worktree/index/tree comparisons; use NUL/raw/name-status output for scripts.
- **`git show-ref`**, **`git get-tar-commit-id`**, **`git var`**, **`git verify-pack`**,
  and **`git show-index`** — read-only metadata and archive/pack helpers.

Newer online references may also expose **`git diff-pairs`**, **`git format-rev`**,
**`git last-modified`**, and **`git repo`**. Treat them as version-gated/experimental
and read their installed manuals before use.

### Transport and server commands

- **`git fetch-pack`** / **`git send-pack`** — low-level client sides of fetch/push.
- **`git upload-pack`** / **`git receive-pack`** — server sides of fetch/push.
- **`git upload-archive`** — server side of remote archive.
- **`git http-backend`** — smart HTTP CGI backend; web-server auth and permissions
  are part of the security boundary.
- **`git daemon`** — simple `git://` server; expose only intended repositories and
  run with least privilege.
- **`git shell`** — restricted SSH command shell for Git hosting; maintain its
  allowlist and account permissions.
- **`git update-server-info`**, **`git http-fetch`**, and **`git http-push`** — legacy
  dumb-HTTP/DAV support; use only when the hosting setup requires it.

Do not recommend server-side commands as if they were client workflow commands.
Consult the server manual and hosting security policy first.

## Helpers, aliases, and extensions

### Internal helpers

`check-attr`, `check-ignore`, `check-mailmap`, `check-ref-format`, `column`,
`credential`, `credential-cache`, `credential-store`, `fmt-merge-msg`, `hook`,
`interpret-trailers`, `mailinfo`, `mailsplit`, `stripspace`, `sh-setup`, `sh-i18n`,
`mergetool--lib`, `web--browse`, and `credential-cache--daemon` support Git plumbing
or scripts. The safe user-facing examples are:

```bash
git check-attr --all -- PATH
git check-ignore -v -- PATH
git check-ref-format --branch NAME
git interpret-trailers --parse < commit-message.txt
git config credential.helper
```

`credential-store` writes credentials to disk, often in plaintext; use a secure OS
helper or SSH where possible. `git hook run NAME` executes code and is not a trust
mechanism by itself.

### Legacy aliases and GUIs

`init-db`→`init`, `fsck-objects`→`fsck`, `stage`→`add`, `annotate`→`blame`, and
`whatchanged`→`log --raw` are compatibility/history entries. `citool`, `gui`, `gitk`,
`gitweb`, `web--browse`, and `mergetool` provide GUI/web layers; their behavior and
security depend on the environment.

### Contributed/external commands

Git LFS (`git lfs`) and `git subtree` can appear in local help but are not core Git
commands. Check their own installed help/documentation. Do not claim that a core Git
command can manage hosting-provider permissions, Actions, merge requests, or LFS
server storage.

## Version gates

Check `git --version` before using these examples. The exact introduction/release
may be distribution-dependent; confirm with `git <command> -h`:

| Feature | Practical gate |
|---|---|
| `switch`, `restore` | Git 2.23+; older workflows use `checkout` |
| `git init -b` | Git 2.28+; otherwise initialize and rename the branch explicitly |
| clone `--filter` | Git 2.19+ plus compatible server support |
| clone `--sparse` | Git 2.25+; verify local help and server/repository support |
| sparse-checkout improvements | Git 2.25+ for modern cone workflow |
| `range-diff` | Git 2.19+ |
| `maintenance` | version-gated; verify `git maintenance -h` |
| `diagnose` | version-gated; verify `git diagnose -h` |
| `version` subcommand/build details | version-gated; verify `git version -h` |
| `scalar` | separate executable in newer Git distributions; verify `scalar -h` |
| `replay`, `refs` | newer/experimental releases; verify locally |
| `backfill`, `history`, `diff-pairs`, `format-rev`, `last-modified`, `repo`, `url-parse` | current online reference may be newer than local Git; treat as experimental/version-gated |

If a command is absent locally, do not emulate it with an unsafe sequence. Explain
the minimum supported alternative and link the manual for the installed version.
