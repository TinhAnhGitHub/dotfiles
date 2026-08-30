# Git usage skill references

Read these files progressively rather than loading the entire catalog for every
question.

| File | Use it for |
|---|---|
| `source-ledger.md` | Source/version scope, local-vs-online drift, and coverage accounting |
| `decision-tree.md` | Fast intent routing and the status/diff/log inspection matrix |
| `workflows.md` | End-to-end recipes for common developer and release scenarios |
| `safety-recovery.md` | Destructive commands, history rewriting, conflicts, and recovery |
| `command-catalog.md` | All command families listed by the official reference, including plumbing |
| `guides-and-book.md` | Official guide map and Pro Git 2nd-edition section/subsection index |
| `command-manifest.json` | Machine-readable command coverage inventory |

## Reading policy

1. Run `git --version` first. Local help is authoritative for installed behavior.
2. Use the command catalog for purpose and risk, then run `git <command> -h` for
   exact flags. Link to the official manual when the choice is version-sensitive.
3. Use the workflows for sequences; adapt branch names, remotes, shell syntax, and
   project policy instead of copying blindly.
4. Use the safety reference before any command that discards files, moves refs,
   rewrites history, deletes remote data, or changes repository configuration.

The references intentionally summarize rather than copy large passages from Pro Git.
See `source-ledger.md` for the official URLs and the documented exceptions.
