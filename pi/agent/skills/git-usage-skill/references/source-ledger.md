# Source ledger and coverage

## Primary sources

- Git reference index: <https://git-scm.com/docs>
- Complete command taxonomy: <https://git-scm.com/docs/git#_git_commands>
- Git command-line conventions: <https://git-scm.com/docs/gitcli>
- Revisions and ranges: <https://git-scm.com/docs/gitrevisions>
- Everyday Git: <https://git-scm.com/docs/giteveryday>
- Workflows: <https://git-scm.com/docs/gitworkflows>
- Glossary: <https://git-scm.com/docs/gitglossary>
- Git FAQ: <https://git-scm.com/docs/gitfaq>
- Pro Git book, 2nd edition: <https://git-scm.com/book/en/v2>
- Pro Git source: <https://github.com/progit/progit2>

The per-command URL convention is
`https://git-scm.com/docs/git-COMMAND`. Scalar is a separately documented executable
at `https://git-scm.com/docs/scalar`; use `scalar -h`. User-facing interfaces use
`https://git-scm.com/docs/NAME` (for example `gitignore`, `githooks`, and
`gitrevisions`).

## Version and environment snapshot

- Research date: 2026-08-08.
- Local executable inspected: Git **2.43.0** (`git --version`, `git help -a`).
- The online reference may describe a newer Git than the local executable. Newer
  commands and flags must be version-gated; do not assume a command exists because it
  appears in the online index.
- Examples commonly use `switch` and `restore` (introduced in Git 2.23); use the
  installed help or the older `checkout` form only when compatibility requires it.
- Commands such as `maintenance`, `diagnose`, `scalar`, `replay`, `refs`, `repo`,
  `backfill`, `history`, `diff-pairs`, `format-rev`, `last-modified`, and `url-parse`
  can vary by installed release. Mark experimental/new commands and verify locally.

## Coverage method

The research used:

1. The live Git reference index and its complete `git(1)` taxonomy.
2. Local `git help -a` and `git <command> -h` for commonly used commands.
3. The live Pro Git table of contents and the upstream Pro Git source headings.
4. Independent delegated reviews for command inventory, workflows, safety, and book
   structure.

`command-manifest.json` records the command names used for coverage checks. The
catalog gives each command a concise purpose, normal workflow role, or an explicit
“advanced plumbing/consult the manual” boundary. Core Git, legacy bridges, server
helpers, and external extensions are deliberately distinguished.

## Pro Git scope

The English second edition exposes 101 live section pages: Chapters 1–10 plus
Appendices A–C. The book-source index in `guides-and-book.md` records all section
titles and all source-level `###`/`####` headings relevant to the operational skill.
The unpublished `subtree-merges.asc` source fragment is called out separately; it has
no corresponding book page.

The book is conceptual and predates many current Git commands. Use it for the model,
workflows, and rationale; use current command manuals and `git -h` for exact behavior,
defaults, security, and newer options.

## Attribution and boundaries

Pro Git is by Scott Chacon and Ben Straub, published by Apress, and is available
under CC BY-NC-SA 3.0 on the official site. This skill contains original summaries,
small examples, and links rather than a reproduction of the book.

Core Git does not include GitHub/GitLab APIs, Git LFS, IDE/GUI behavior, or hosting
permissions. Mention those boundaries when a user asks for provider-specific actions.
