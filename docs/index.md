# Docs Index

Living design docs now live in [`docs/design/`](design/index.md) (per-feature
behavior specs) and [`docs/prd.md`](prd.md) (product goals and scope). They are
written and updated by the `task-splitter` and `implementation-workflow`
plugins.

Architecture decisions live in [`docs/adr/`](adr/) — one numbered ADR per
decision that would take a human half a day or more to reverse. Lighter
rationale lives in source comments (when it's local to one file) or in commit
message bodies (when it spans several); implementation narrative lives in the
PR that shipped it. See each plugin's `docs/vcs-minimalism.md` for the full
rule.

The decision records and incident logs below predate all of that and are kept
as historical reference only — no new entries are added to these two
directories.

## Decision Records (historical)

| Task | ADR | Summary |
|------|-----|---------|
| task-20260308-223337 | [ADR](decision-records/task-20260308-223337-adr.md) | Dev-Workflow Plugin Documentation & Orchestrator UX |

## Incident Logs (historical)

| Task | Log | Summary |
|------|-----|---------|
| task-20260308-223337 | [Log](incident-logs/task-20260308-223337-log.md) | Out-of-scope edits, rate limit recovery, typo from substitution |
