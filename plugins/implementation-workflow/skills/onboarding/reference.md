# Onboarding — Extended Reference

## 1. Auto-Detection Heuristics for Test / Lint / Build Commands

Check for these manifest files, in order, and propose the corresponding
commands. Multiple may apply in a polyglot repo — propose all that match.

| Manifest found | Test Command | Lint / Build Commands |
|---|---|---|
| `package.json` with a `scripts.test` | `npm test` (or `pnpm test` / `yarn test` — check for `pnpm-lock.yaml` / `yarn.lock` to pick the right runner) | `scripts.lint`, `scripts.build` if present |
| `Makefile` with a `test:` target | `make test` | `make lint`, `make build` if those targets exist |
| `pyproject.toml` | `pytest` (or the tool under `[tool.pytest]`/`[tool.hatch.envs.*.scripts]` if specified) | `ruff check` / `black --check` if configured, `python -m build` |
| `go.mod` | `go test ./...` | `go vet ./...`, `go build ./...` |
| `Cargo.toml` | `cargo test` | `cargo clippy`, `cargo build` |
| `Gemfile` with rspec | `bundle exec rspec` | `bundle exec rubocop` if configured |

If nothing matches, ask the user directly rather than leaving the section
blank without asking — an empty Test Command silently degrades `test-writer`'s
red-confirmation step, and with it the whole test-first gate, to "no automated
verification". That should be a deliberate choice, not a default that falls out
of a missed detection.

Both are plain shell commands, not tools with their own identity, so neither
gets a `docs/tools/<tool-slug>.md`. They're written directly into whichever
consumer file §3 names.

## 2. What NOT to Auto-Fill

A code-search MCP, a library/docs MCP, and a verification MCP are never
inferable from repo files — an MCP server's presence is a matter of the
user's local Claude Code configuration, not something checked into the repo.
Always ask; never guess a plausible-sounding tool name here.

## 3. The Fixed Agent ↔ Tool Mapping

This is the table Step 4 writes against, and the one Step 3's migration path
uses to carry an old `docs/tool.md` section onto the new per-file layout. It
is fixed by the plugin's design, not something onboarding asks the user to
redraw — only *whether a tool exists* is the user's answer, never *who reads
it*.

| Tool category | Consumer file(s) that reference it |
|---|---|
| Test Command | `docs/tools/test-writer.md`, `docs/tools/implementation-planning.md` |
| Lint / Build Commands | `docs/tools/implementer.md` |
| Code Search Tool (MCP or CLI) | `docs/tools/repository-explorer.md` |
| Library / Docs Tool (MCP) | `docs/tools/library-researcher.md` |
| Verification Tool (MCP) | `docs/tools/test-writer.md`, `docs/tools/implementation-planning.md`, `docs/tools/implementer.md`, `docs/tools/code-reviewer.md`, `docs/tools/test-reviewer.md` |

Notes:

- A tool referenced by more than one consumer (Test Command, Verification
  Tool) gets exactly one `docs/tools/<tool-slug>.md`, and each consumer file
  gets its own short paragraph pointing at it — in that consumer's own words,
  per [../implementation-workflow/templates/agent-tool-template.md](../implementation-workflow/templates/agent-tool-template.md).
  Do not merge those paragraphs into a shared file; the whole reason for the
  per-consumer split is that `library-researcher`'s reason for using a tool
  and `repository-explorer`'s are different questions, even on the rare
  occasion the same tool could answer both — see the real-world case this
  layout was designed to prevent, where a single shared "Code Search Tools"
  section caused a docs-lookup MCP to be miscategorized as a codebase-search
  tool.
- `persistence-engineer`, the orchestrator skill itself, `requirement-understanding`,
  and `onboarding` are not in this table. They only check whether `docs/tools/`
  exists at all; they don't select a tool, so they have no consumer file of
  their own.
- A tool named under "anything else" in Step 4.3 that the user says is
  informational-only gets a `docs/tools/<tool-slug>.md` but no row here and no
  consumer file — it exists for a human to read, not for a specific agent to
  reach for.

## 4. Re-running Onboarding

This skill is idempotent — safe to re-run whenever the project's tooling
changes (a new lint command added, a verification MCP newly configured).
Step 3's present/missing branches, and Step 4's "update it" path re-using a
file's existing content as the default, handle the first-run, update, and
migration cases without needing separate logic.
