# Architecture Decision Records

One numbered ADR per decision that would take a human half a day or more to
reverse. Anything lighter belongs in a source comment (reasoning local to one
file) or a commit message body (reasoning spanning several) — see each plugin's
`docs/vcs-minimalism.md` for the routing rule.

Files are `NNNN-<kebab-slug>.md`, zero-padded to four digits. Numbers are never
reused, even when an ADR is superseded. **This index is updated in the same
commit as the ADR it describes** — an index that disagrees with the files is
worse than no index.

| # | Decision | Status | Date |
|---|----------|--------|------|

Statuses: `draft` → `accepted`, then `superseded by ADR-NNNN` or `deprecated`.
Once an ADR leaves `draft`, its `Context` and `Decision` are immutable; a
change of mind is a new ADR that supersedes it.

`docs/decision-records/` holds pre-ADR history and takes no new entries.
