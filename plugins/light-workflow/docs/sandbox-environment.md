# Sandbox Environment — What This Run Can Touch

Shared policy. Every file write and network call this plugin makes happens
inside a sandboxed environment with fixed constraints. This document is those
constraints, not a suggestion — a command that ignores them fails, or
silently does the wrong thing.

This document mirrors the copy in the `implementation-workflow` plugin. Both
plugins install independently, so each carries its own copy; **if you change
one, change both.** The constraints themselves are identical — only §6 ("Who
reads this") differs: this plugin has no subagents, so the orchestrator skill
is the only reader.

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
writable here, so don't reach for it out of habit. When Phase 2 needs a
scratch or temporary file, write it under a `.tmp/` directory at the project
root instead — create it if it doesn't exist, keep it out of version control
(gitignored, never staged), and never rely on it surviving past this run.
This plugin keeps no workspace files of its own, so this only ever comes up
for genuinely throwaway scratch work.

## 3. Network

Direct network connections — `git`, `gh`, `curl`, a raw HTTP client, anything
that opens a socket itself — reach only `github.com` (and its subdomains, e.g.
`api.github.com`). Every other host is blocked at the network layer; the
connection simply fails, not silently degrades.

| Path | Reaches |
|---|---|
| `git` / `gh` / `curl` / direct sockets | `github.com` only |
| `WebFetch` / `WebSearch` | any host |

`WebFetch` and `WebSearch` are the sanctioned exception: they reach other
hosts because they run through a different path than a direct connection. If
Phase 2 needs to look something up outside the codebase — a library's docs, an
API reference — that has to go through `WebFetch`/`WebSearch`, never a direct
fetch.

## 4. Pre-existing device-file artifacts

`git status` in this environment may show untracked files at the repository
root — `.git/config`, `.zshrc`, `.bashrc`, `.gitconfig`, and similar. These are
sandbox-created files bound to `/dev/null`, put there to keep unintended
effects inside the process tree. They are not real project files and not
someone's work in progress — do not investigate them as if they were, and
don't let them read as a dirty working tree at Phase 0.

**Ignore them, and never stage them.** This is one more reason staging is
always explicit in this plugin (Phase 4) — `git add -A` and `git add .` are
never used, since either would sweep these artifacts into a commit.

## 5. `git push` cannot register upstream

`git push -u origin ...` (or `--set-upstream`) cannot establish tracking in
this environment — a consequence of §3's egress restriction. Never rely on
`-u`, and never push a bare `HEAD` expecting a remembered upstream: **name the
branch explicitly on every push**, including a second push after a
request-changes round on the same branch.

```bash
git push origin "<branch-name>"                     # every push, first or not
git push --force-with-lease origin "<branch-name>"  # after amending an already-pushed branch
```

Wherever another part of this plugin shows `git push -u origin HEAD` as an
example, this section supersedes it.

## 6. Who reads this

There is one reader: the `light-workflow` orchestrator skill itself, at Step
0, before Phase 0 runs. It governs everything the orchestrator does inline —
Phase 0's branch setup, Phase 2's file writes and any `WebFetch`/`WebSearch`
lookups, and Phase 4's commit, push, and PR.
