# Official guides and Pro Git coverage map

This file is a routing index, not a copy of the book. It records every live Pro Git
2nd-edition page and the source-level subsections researched for this skill. Read the
linked page when a user asks for historical rationale, a full tutorial, or a
provider/tool-specific detail. Use current Git manuals for exact flags.

## Official Git guides and interfaces

| Topic | Official page | Route when |
|---|---|---|
| CLI conventions | [`gitcli`](https://git-scm.com/docs/gitcli) | option order, `--`, pathspecs, quoting |
| revisions/ranges | [`gitrevisions`](https://git-scm.com/docs/gitrevisions) | `HEAD~`, `^`, reflogs, `..`, `...`, `^{}` |
| everyday command set | [`giteveryday`](https://git-scm.com/docs/giteveryday) | choose a normal daily command sequence |
| workflow design | [`gitworkflows`](https://git-scm.com/docs/gitworkflows) | integration branches and publication policy |
| tutorial | [`gittutorial`](https://git-scm.com/docs/gittutorial), [`gittutorial-2`](https://git-scm.com/docs/gittutorial-2) | learn the basics from first principles |
| glossary | [`gitglossary`](https://git-scm.com/docs/gitglossary) | clarify Git terminology |
| FAQ | [`gitfaq`](https://git-scm.com/docs/gitfaq) | common behavior questions |
| ignore rules | [`gitignore`](https://git-scm.com/docs/gitignore) | why a path is tracked/ignored |
| attributes | [`gitattributes`](https://git-scm.com/docs/gitattributes) | line endings, binary, filters, merge/diff drivers |
| hooks | [`githooks`](https://git-scm.com/docs/githooks) | client/server hook behavior and trust |
| submodules | [`gitsubmodules`](https://git-scm.com/docs/gitsubmodules), [`gitmodules`](https://git-scm.com/docs/gitmodules) | nested repositories and gitlinks |
| credentials | [`gitcredentials`](https://git-scm.com/docs/gitcredentials), [credential helpers](https://git-scm.com/doc/credential-helpers) | authentication storage and helpers |
| repository layout | [`gitrepository-layout`](https://git-scm.com/docs/gitrepository-layout) | `.git` internals and bare repositories |
| diff machinery | [`gitdiffcore`](https://git-scm.com/docs/gitdiffcore) | diffcore/rename/filter internals |
| core tutorial | [`gitcore-tutorial`](https://git-scm.com/docs/gitcore-tutorial) | plumbing and object model |
| namespaces/remotes | [`gitnamespaces`](https://git-scm.com/docs/gitnamespaces), [`gitremote-helpers`](https://git-scm.com/docs/gitremote-helpers) | hosting/transport internals |
| CVS migration | [`gitcvs-migration`](https://git-scm.com/docs/gitcvs-migration) | legacy SCM migration |

Developer-only format/protocol pages include `gitformat-bundle`, `gitformat-chunk`,
`gitformat-commit-graph`, `gitformat-index`, `gitformat-pack`, `gitformat-signature`,
`protocol-capabilities`, `protocol-common`, `protocol-http`, `protocol-pack`, and
`protocol-v2`. Use them only for implementation or transport debugging.

## Pro Git map: Chapters 1–3

### 1. Getting Started

Page: <https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control>

- **1.1 About Version Control** — local, centralized, and distributed version control systems.
- **1.2 A Short History of Git** — why Git's distributed/content-addressed design exists.
- **1.3 What is Git?** — snapshots, local operations, integrity, append-only tendencies,
  and the three states: worktree, index, and repository.
  - Snapshots, Not Differences; Nearly Every Operation is Local; Git Has Integrity;
    Git Generally Only Adds Data; The Three States.
- **1.4 The Command Line** — use the CLI as the common denominator across tools.
- **1.5 Installing Git** — Linux, macOS, Windows, and source installation.
  - Installing on Linux; Installing on macOS; Installing on Windows; Installing from Source.
- **1.6 First-Time Git Setup** — identity, editor, default branch, and checking settings.
  - Your Identity; Your Editor; Your default branch name; Checking Your Settings.
- **1.7 Getting Help** — `git help`, `git <command> -h`, and online manuals.
- **1.8 Summary** — chapter recap.

### 2. Git Basics

Page: <https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository>

- **2.1 Getting a Git Repository** — initialize an existing directory or clone one.
  - Initializing a Repository in an Existing Directory; Cloning an Existing Repository.
- **2.2 Recording Changes to the Repository** — inspect, track, stage, ignore, commit,
  remove, and move files.
  - Checking the Status of Your Files; Tracking New Files; Staging Modified Files;
    Short Status; Ignoring Files; Viewing Your Staged and Unstaged Changes;
    Committing Your Changes; Skipping the Staging Area; Removing Files; Moving Files.
- **2.3 Viewing the Commit History** — log formatting and history limits.
  - Limiting Log Output.
- **2.4 Undoing Things** — unstage, restore, and choose safe versus rewriting undo.
  - Unstaging a Staged File; Unmodifying a Modified File; Undoing things with `git restore`.
- **2.5 Working with Remotes** — inspect/add/fetch/pull/push/rename/remove remotes.
  - Showing Your Remotes; Adding Remote Repositories; Fetching and Pulling from Your
    Remotes; Pushing to Your Remotes; Inspecting a Remote; Renaming and Removing Remotes.
- **2.6 Tagging** — list, annotate, create, share, delete, and check out tags.
  - Listing Your Tags; Creating Tags; Annotated Tags; Lightweight Tags; Tagging Later;
    Sharing Tags; Deleting Tags; Checking out Tags.
- **2.7 Git Aliases** — configure concise aliases while keeping the underlying command clear.
- **2.8 Summary** — chapter recap.

### 3. Git Branching

Page: <https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell>

- **3.1 Branches in a Nutshell** — refs are movable pointers; create and switch safely.
  - Creating a New Branch; Switching Branches.
- **3.2 Basic Branching and Merging** — topic work, basic merges, and conflict states.
  - Basic Branching; Basic Merging; Basic Merge Conflicts.
- **3.3 Branch Management** — list, inspect, delete, rename, and set upstream branches.
  - Changing a branch name.
- **3.4 Branching Workflows** — long-running integration branches and topic branches.
  - Long-Running Branches; Topic Branches.
- **3.5 Remote Branches** — pushing, tracking, pulling, and deleting remote branches.
  - Pushing; Tracking Branches; Pulling; Deleting Remote Branches.
- **3.6 Rebasing** — basic/more interesting rebase, its perils, the golden rule, and
  rebase versus merge.
  - The Basic Rebase; More Interesting Rebases; The Perils of Rebasing; Rebase When
    You Rebase; Rebase vs. Merge.
- **3.7 Summary** — chapter recap.

## Pro Git map: Chapters 4–6

### 4. Git on the Server

Page: <https://git-scm.com/book/en/v2/Git-on-the-Server-The-Protocols>

- **4.1 The Protocols** — local, HTTP, SSH, and Git protocols.
  - Local Protocol; The HTTP Protocols; The SSH Protocol; The Git Protocol;
    protocol advantages/disadvantages, Smart HTTP, and Dumb HTTP.
- **4.2 Getting Git on a Server** — bare repositories and small SSH setups.
  - Putting the Bare Repository on a Server; Small Setups; SSH Access.
- **4.3 Generating Your SSH Public Key** — create and install an SSH identity.
- **4.4 Setting Up the Server** — permissions and server-side repository setup.
- **4.5 Git Daemon** — simple read-only Git transport and its exposure boundary.
- **4.6 Smart HTTP** — HTTP transport and web-server integration.
- **4.7 GitWeb** — web browsing of repository history.
- **4.8 GitLab** — installation, administration, basic usage, and collaboration.
  - Installation; Administration; Basic Usage; Working Together; Users; Groups;
    Projects; Hooks.
- **4.9 Third Party Hosted Options** — hosted service choices; provider behavior is
  outside core Git.
- **4.10 Summary** — chapter recap.

### 5. Distributed Git

Page: <https://git-scm.com/book/en/v2/Distributed-Git-Distributed-Workflows>

- **5.1 Distributed Workflows** — centralized, integration-manager, and dictator/
  lieutenants models, plus source-branch patterns.
  - Centralized Workflow; Integration-Manager Workflow; Dictator and Lieutenants
    Workflow; Patterns for Managing Source Code Branches; Workflows Summary.
- **5.2 Contributing to a Project** — commit guidelines and private/public/email
  contribution patterns.
  - Commit Guidelines; Private Small Team; Private Managed Team; Forked Public
    Project; Public Project over Email; Summary.
- **5.3 Maintaining a Project** — topic branches, patches, remote branches, deciding
  what was introduced, integration, release tags, builds, releases, and shortlog.
  - Working in Topic Branches; Applying Patches from Email; Checking Out Remote
    Branches; Determining What Is Introduced; Integrating Contributed Work; Tagging
    Your Releases; Generating a Build Number; Preparing a Release; The Shortlog;
    applying patches with `apply` or `am`, merge workflows, large merges, rebase/
    cherry-pick workflows, and rerere.
- **5.4 Summary** — chapter recap.

### 6. GitHub

Page: <https://git-scm.com/book/en/v2/GitHub-Account-Setup-and-Configuration>

- **6.1 Account Setup and Configuration** — SSH access, avatars, email addresses,
  and two-factor authentication.
  - SSH Access; Your Avatar; Your Email Addresses; Two Factor Authentication.
- **6.2 Contributing to a Project** — forks, GitHub Flow, pull requests, Markdown,
  and keeping a fork current.
  - Forking Projects; The GitHub Flow; Advanced Pull Requests; GitHub Flavored
    Markdown; Keep your GitHub public repository up-to-date; creating and iterating
    on a pull request, pull requests as patches, and keeping up with upstream;
    references, task lists, code snippets, quoting, emoji, and images.
- **6.3 Maintaining a Project** — repositories, collaborators, pull requests,
  notifications, special files, README/CONTRIBUTING, and administration.
  - Creating a New Repository; Adding Collaborators; Managing Pull Requests;
    Mentions and Notifications; Special Files; README; CONTRIBUTING; Project
    Administration; email/collaboration/pull-request references and notification pages.
- **6.4 Managing an organization** — organization basics, teams, and audit log.
  - Organization Basics; Teams; Audit Log.
- **6.5 Scripting GitHub** — services, hooks, API usage, issue comments, PR status,
  and Octokit.
  - Services and Hooks; The GitHub API; Basic Usage; Commenting on an Issue; Changing
    the Status of a Pull Request; Octokit; Services; Hooks.
- **6.6 Summary** — chapter recap.

## Pro Git map: Chapter 7

### 7. Git Tools

Page: <https://git-scm.com/book/en/v2/Git-Tools-Revision-Selection>

- **7.1 Revision Selection** — single revisions, short IDs, branches, reflog names,
  ancestry, and commit ranges.
  - Single Revisions; Short SHA-1; Branch References; RefLog Shortnames; Ancestry
    References; Commit Ranges; Double Dot; Multiple Points; Triple Dot.
- **7.2 Interactive Staging** — stage/unstage files and patches.
  - Staging and Unstaging Files; Staging Patches.
- **7.3 Stashing and Cleaning** — stash work, creative stash uses, branch from a
  stash, and clean the working directory.
  - Stashing Your Work; Creative Stashing; Creating a Branch from a Stash; Cleaning
    your Working Directory.
- **7.4 Signing Your Work** — GPG introduction, signed tags/commits, verification,
  and team signing policy.
  - GPG Introduction; Signing Tags; Verifying Tags; Signing Commits; Everyone Must Sign.
- **7.5 Searching** — content search and history search.
  - Git Grep; Git Log Searching; Line Log Search.
- **7.6 Rewriting History** — amend, edit messages/order/squash/split/delete, and
  the nuclear filter-branch option.
  - Changing the Last Commit; Changing Multiple Commit Messages; Reordering Commits;
    Squashing Commits; Splitting a Commit; Deleting a commit; The Nuclear Option:
    filter-branch; removing a file from every commit, making a subdirectory the root,
    and changing email addresses globally.
- **7.7 Reset Demystified** — three trees, reset workflow/roles, paths, squashing,
  and checkout comparison.
  - The Three Trees; The Workflow; The Role of Reset; Reset With a Path; Squashing;
    Check It Out; Summary; HEAD; Index; Working Directory; steps 1/2/3; Recap;
    Without Paths; With Paths.
- **7.8 Advanced Merging** — conflict inspection, merge undo, and alternative merges.
  - Merge Conflicts; Undoing Merges; Other Types of Merges; Aborting a Merge;
    Ignoring Whitespace; Manual File Re-merging; Checking Out Conflicts; Merge Log;
    Combined Diff Format; Fix the references; Reverse the commit; Our or Theirs Preference.
- **7.9 Rerere** — record and reuse conflict resolutions with review.
- **7.10 Debugging with Git** — line annotation and binary search.
  - File Annotation; Binary Search.
- **7.11 Submodules** — nested repository lifecycle and failure modes.
  - Starting with Submodules; Cloning a Project with Submodules; Working on a Project
    with Submodules; Pulling in Upstream Changes from the Submodule Remote; Pulling
    Upstream Changes from the Project Remote; Working on a Submodule; Publishing
    Submodule Changes; Merging Submodule Changes; Submodule Tips; Submodule Foreach;
    Useful Aliases; Issues with Submodules; Switching branches; Switching from
    subdirectories to submodules.
- **7.12 Bundling** — offline object/ref transfer with bundle files.
- **7.13 Replace** — replacement refs for controlled history experiments.
- **7.14 Credential Storage** — credential helper behavior and custom caching.
  - Under the Hood; A Custom Credential Cache.
- **7.15 Summary** — chapter recap.

The source repository also has an orphaned `subtree-merges.asc` fragment with a single
“Subtree Merging” heading. It is not included in the published book and has no live
book page; do not present it as a normal Pro Git section.

## Pro Git map: Chapters 8–10

### 8. Customizing Git

Page: <https://git-scm.com/book/en/v2/Customizing-Git-Git-Configuration>

- **8.1 Git Configuration** — client/server settings, colors, editors, tools,
  formatting, whitespace, and policy.
  - Basic Client Configuration; Colors in Git; External Merge and Diff Tools;
    Formatting and Whitespace; Server Configuration; `core.editor`,
    `commit.template`, `core.pager`, `user.signingkey`, `core.excludesfile`,
    `help.autocorrect`, `color.ui`, `color.*`, `core.autocrlf`, `core.whitespace`,
    `receive.fsckObjects`, `receive.denyNonFastForwards`, `receive.denyDeletes`.
- **8.2 Git Attributes** — binary detection, keyword expansion, export rules, merge
  strategies, and diff drivers.
  - Binary Files; Keyword Expansion; Exporting Your Repository; Merge Strategies;
    Identifying Binary Files; Diffing Binary Files; `export-ignore`; `export-subst`.
- **8.3 Git Hooks** — installation, client-side hooks, and server-side hooks.
  - Installing a Hook; Client-Side Hooks; Server-Side Hooks; committing-workflow
    hooks; email-workflow hooks; other client hooks; `pre-receive`; `update`;
    `post-receive`.
- **8.4 An Example Git-Enforced Policy** — server/client policy implementation and
  testing.
  - Server-Side Hook; Client-Side Hooks; commit-message format; user ACL system;
    Testing It Out.
- **8.5 Summary** — chapter recap.

### 9. Git and Other Systems

Page: <https://git-scm.com/book/en/v2/Git-and-Other-Systems-Git-as-a-Client>

- **9.1 Git as a Client** — interoperability with Subversion, Mercurial, and Perforce.
  - Git and Subversion: `git svn`, setup, getting started, committing back, pulling
    changes, branching issues, SVN branching, creating an SVN branch, switching
    active branches, Subversion commands, Git-SVN summary.
  - Git and Mercurial: `git-remote-hg`, getting started, workflow, branches and
    bookmarks, Mercurial summary.
  - Git and Perforce: Git Fusion, `git-p4`, and Git/Perforce summary.
- **9.2 Migrating to Git** — migration from Subversion, Mercurial, Perforce, or a
  custom importer.
  - Subversion; Mercurial; Perforce; Perforce Git Fusion; Git-p4; A Custom Importer.
- **9.3 Summary** — chapter recap.

### 10. Git Internals

Page: <https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain>

- **10.1 Plumbing and Porcelain** — user-facing commands versus low-level building
  blocks; use plumbing for controlled tooling, not casual edits.
- **10.2 Git Objects** — blobs, trees, commits, and object storage.
  - Tree Objects; Commit Objects; Object Storage.
- **10.3 Git References** — refs, `HEAD`, tags, and remotes.
  - The HEAD; Tags; Remotes.
- **10.4 Packfiles** — object packing and storage efficiency.
- **10.5 The Refspec** — mapping refs during fetch and push.
  - Pushing Refspecs; Deleting References.
- **10.6 Transfer Protocols** — dumb/smart transport and protocol summaries.
  - The Dumb Protocol; The Smart Protocol; Protocols Summary; uploading/downloading
    data; SSH; HTTP(S).
- **10.7 Maintenance and Data Recovery** — maintenance, recovery, and object removal.
  - Maintenance; Data Recovery; Removing Objects.
- **10.8 Environment Variables** — process-wide Git controls.
  - Global Behavior; Repository Locations; Pathspecs; Committing; Networking;
    Diffing and Merging; Debugging; Miscellaneous.
- **10.9 Summary** — chapter recap.

## Pro Git map: Appendices

### Appendix A. Git in Other Environments

Page: <https://git-scm.com/book/en/v2/Appendix-A:-Git-in-Other-Environments-Graphical-Interfaces>

This appendix is platform/tool-specific. Route here only when a user asks about the
listed GUI or shell integration, and keep core CLI behavior separate.

- **A1.1 Graphical Interfaces** — `gitk`, `git-gui`, GitHub desktop clients, and other GUIs.
  - `gitk` and `git-gui`; GitHub for macOS and Windows; Other GUIs; installation,
    recommended workflow, and summary.
- **A1.2 Git in Visual Studio**.
- **A1.3 Git in Visual Studio Code**.
- **A1.4 Git in IntelliJ / PyCharm / WebStorm / PhpStorm / RubyMine**.
- **A1.5 Git in Sublime Text**.
- **A1.6 Git in Bash**.
- **A1.7 Git in Zsh**.
- **A1.8 Git in PowerShell** — includes installation and prerequisites/platform setup.
  - Installation; prerequisites (Windows only); PowerShell Gallery; update prompt;
    from source.
- **A1.9 Summary**.

### Appendix B. Embedding Git in your Applications

Page: <https://git-scm.com/book/en/v2/Appendix-B:-Embedding-Git-in-your-Applications-Command-line-Git>

- **A2.1 Command-line Git** — invoke the CLI as an application boundary.
- **A2.2 Libgit2** — library usage, bindings, and further reading.
  - Advanced Functionality; Other Bindings; Further Reading; LibGit2Sharp;
    objective-git; pygit2.
- **A2.3 JGit** — setup, plumbing, porcelain, and further reading.
  - Getting Set Up; Plumbing; Porcelain; Further Reading.
- **A2.4 go-git** — advanced functionality and further reading.
- **A2.5 Dulwich** — further reading.

There is no published Appendix B summary page.

### Appendix C. Git Commands

Page: <https://git-scm.com/book/en/v2/Appendix-C:-Git-Commands-Setup-and-Config>

The appendix is a categorized quick reference, not a replacement for current
manuals. Its 12 pages are:

- **A3.1 Setup and Config** — `git config`, editor settings, `git help`.
- **A3.2 Getting and Creating Projects** — `git init`, `git clone`.
- **A3.3 Basic Snapshotting** — `git add`, `status`, `diff`, `difftool`, `commit`,
  `reset`, `rm`, `mv`, `clean`.
- **A3.4 Branching and Merging** — `branch`, `checkout`, `merge`, `mergetool`,
  `log`, `stash`, `tag`.
- **A3.5 Sharing and Updating Projects** — `fetch`, `pull`, `push`, `remote`,
  `archive`, `submodule`.
- **A3.6 Inspection and Comparison** — `show`, `shortlog`, `describe`.
- **A3.7 Debugging** — `bisect`, `blame`, `grep`.
- **A3.8 Patching** — `cherry-pick`, `rebase`, `revert`.
- **A3.9 Email** — `apply`, `am`, `format-patch`, `imap-send`, `send-email`,
  `request-pull`.
- **A3.10 External Systems** — `svn`, `fast-import`.
- **A3.11 Administration** — `gc`, `fsck`, `reflog`, `filter-branch`.
- **A3.12 Plumbing Commands** — low-level object/index/ref operations.

There is no published Appendix C summary page.

## Operational takeaways distilled from the book

1. Git stores snapshots and refs, not a linear list of file diffs; this explains why
   branches are cheap and why object IDs change after a rebase.
2. The index is a deliberate proposed next snapshot. `add -p` and the staged diff
   are review tools, not merely ceremony.
3. Fetching and integrating are separate decisions. Remote-tracking refs are local
   bookmarks until refreshed.
4. Branch names are movable refs. A branch backup is a cheap recovery anchor before
   a rewrite.
5. Rebasing is useful for private patch series; its golden rule is not to rebase
   commits that others may have based work on.
6. Public contribution models differ: centralized, integration-manager, fork/PR,
   and email patch flows all use the same object/ref primitives.
7. A merge records topology; a rebase recreates commits. Choose based on history
   ownership and review policy, not aesthetic preference alone.
8. `reset`, `restore`, and `revert` act on different trees/ref histories; ask what
   the user wants to preserve before choosing one.
9. `reflog` and dangling objects can recover local history, but reflogs expire and
   untracked never-staged files may be unrecoverable.
10. Submodules pin a commit in a separate repository; the superproject does not store
    the submodule's current branch or working files.
11. Attributes, ignore rules, hooks, filters, and credentials change behavior at the
    repository/config boundary; inspect them before trusting a result.
12. Plumbing commands expose Git's object/ref/index model but can bypass normal safety
    checks; use them for scripts and diagnostics with validation and atomic updates.
