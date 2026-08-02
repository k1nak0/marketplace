# Onboarding — Extended Reference

## Auto-Detection Heuristics for `docs/tool.md`

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
blank without asking — an empty Test Command silently degrades
`feature-developer`'s Red→Green loop to "no automated verification," which
should be a deliberate choice, not a default from a missed detection.

## What NOT to Auto-Fill

Code Search Tools (MCP) and Verification Tools (MCP) are never inferable
from repo files — an MCP server's presence is a matter of the user's local
Claude Code configuration, not something checked into the repo. Always ask;
never guess a plausible-sounding tool name here.

## Re-running Onboarding

This skill is idempotent — safe to re-run whenever the project's tooling
changes (a new lint command added, a verification MCP newly configured).
Step 2's present/missing branch handles both the first-run and update case
without needing separate logic.
