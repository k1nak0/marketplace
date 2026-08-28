# Sandbox Environment — What This Run Can Touch

Shared policy. Every agent and skill in this plugin that reads a file, writes a
file, or makes a network call runs inside a sandboxed environment with fixed
constraints. This document is those constraints, not a suggestion — a
command that ignores them fails, or silently does the wrong thing.

This document mirrors the copy in the `light-workflow` plugin. Both plugins
install independently, so each carries its own copy; **if you change one,
change both.** The constraints themselves are identical — only §6 ("Who reads
this") differs, because `light-workflow` has no subagents.

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
writable here, so don't reach for it out of habit. When a phase needs a
scratch or temporary file, write it under a `.tmp/` directory at the project
root instead — create it if it doesn't exist, keep it out of version control
(gitignored, never staged), and never rely on it surviving past this run.

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
hosts because they run through a different path than a direct connection.
`library-researcher` (Phase 5) lives entirely inside this exception — its
retrieval of external library documentation is only possible because it goes
through `WebFetch`/`WebSearch`, never a direct fetch, and the same applies to
any project-specific docs MCP tool it uses instead.

## 4. Pre-existing device-file artifacts

`git status` in this environment may show untracked files at the repository
root — `.git/config`, `.zshrc`, `.bashrc`, `.gitconfig`, and similar. These are
sandbox-created files bound to `/dev/null`, put there to keep unintended
effects inside the process tree. They are not real project files and not
someone's work in progress — do not investigate them as if they were.

**Ignore them, and never stage them.** This is one more reason `git add -A`
and `git add .` are never used in this pipeline (`git-workflow.md` §5):
either would sweep these artifacts into a commit. Stage explicit paths only.

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

Every agent that writes a file or touches the network —
`repository-explorer`, `library-researcher`, `test-writer`, `implementer`,
`code-reviewer`, `persistence-engineer` — and every skill that does the same
inline: the `implementation-workflow` orchestrator itself (Step 0, before
anything else runs), `requirement-understanding`, `issue-refinement`,
`implementation-planning`, and `onboarding`.
