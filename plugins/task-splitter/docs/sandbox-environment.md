# Sandbox Environment — What This Run Can Touch

Shared policy. Every skill in this plugin that reads a file, writes a file, or
makes a network call runs inside a sandboxed environment with fixed
constraints. This document is those constraints, not a suggestion — a command
that ignores them fails, or silently does the wrong thing.

This document mirrors the copies in the `implementation-workflow` and
`light-workflow` plugins. All three install independently, so each carries its
own copy; **if you change one, change all three.** The constraints themselves
are identical — only §6 ("Who reads this") differs, because each plugin has a
different set of readers.

---

## 1. Filesystem — read

Reading is unrestricted. Any path, anywhere on disk, may be read at any time.
There is no location this rule treats as off-limits, and no phase needs to
justify a read.

## 2. Filesystem — write

Writes are restricted to two locations:

| Location | Writable? |
|---|---|
| This project's working tree | Yes |
| `~/.claude/projects/` (cross-session memory, not run output) | Yes |
| `$TMPDIR` / `/tmp` | **No** |
| Anywhere else | No |

`$TMPDIR` is a common scratch location in other environments; it is **not**
writable here, so don't reach for it out of habit. This plugin's own scratch
already lives inside the working tree, under
`.claude/task-splitter/<task-id>/` — that is where a run's intermediate files
go, and it is never staged. If a phase needs something more throwaway than
that, write it under a `.tmp/` directory at the project root, keep it out of
version control, and never rely on it surviving past this run.

## 3. Network

Direct network connections — `git`, `gh`, `curl`, a raw HTTP client, anything
that opens a socket itself — reach only `github.com` (and its subdomains, e.g.
`api.github.com`). Every other host is blocked at the network layer; the
connection simply fails, not silently degrades.

| Path | Reaches |
|---|---|
| `git` / `gh` / `curl` / direct sockets | `github.com` only |
| `WebFetch` / `WebSearch` | any host |

`gh` is inside the allowance, which is why Phase 5's Issue registration and
Phase 4's PR both work. `WebFetch` and `WebSearch` are the sanctioned
exception in the other direction: they reach other hosts because they run
through a different path than a direct connection. If a phase needs to look
something up outside the codebase and outside GitHub — a standard, a vendor's
API contract that a constraint depends on — that has to go through
`WebFetch`/`WebSearch`, never a direct fetch.

## 4. Pre-existing device-file artifacts

`git status` in this environment may show untracked files at the repository
root — `.git/config`, `.zshrc`, `.bashrc`, `.gitconfig`, and similar. These are
sandbox-created files bound to `/dev/null`, put there to keep unintended
effects inside the process tree. They are not real project files and not
someone's work in progress — do not investigate them as if they were.

**Ignore them, and never stage them.** They are also why the working-tree
cleanliness check before Phase 2 uses `git status --porcelain -- . ':!.claude'`
and still needs a human eye rather than an emptiness test, and one more reason
`git add -A` and `git add .` are never used in this plugin
(`vcs-minimalism.md` §5): either would sweep these artifacts into a commit.
Stage explicit paths only.

## 5. `git push` cannot register upstream

`git push -u origin ...` (or `--set-upstream`) cannot establish tracking in
this environment — a consequence of §3's egress restriction. Never rely on
`-u`, and never push a bare `HEAD` expecting a remembered upstream: **name the
branch explicitly on every push**, including the second and later pushes on
the same branch.

```bash
git push origin "<branch-name>"                     # every push, first or not
git push --force-with-lease origin "<branch-name>"  # after a rewrite of a pushed branch
```

Wherever another doc in this plugin shows `git push -u origin HEAD` as an
example, this section supersedes it.

## 6. Who reads this

The `task-splitter` orchestrator skill reads it at Step 0, before anything else
runs, and it governs every phase from there. The four sub-skills read it too,
because each one writes files or calls the network:
`understand-requirements` (writes the task directory),
`design-behavior` (writes `docs/design/`), `plan-tasks` (writes the breakdown),
and `register-tasks` (`gh`, throughout).
