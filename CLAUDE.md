# CLAUDE.md

This file provides AI agent context for the k1nak0/marketplace repository.

---

## task-splitter Plugin

Takes an epic to a GitHub Map Issue plus per-task Issues, writing the
behavior-only design doc on the way when one doesn't exist yet. Entry point:
`/task-splitter:task-splitter` (the orchestrator skill lives at
`skills/task-splitter/`).

**It runs in one of two modes**, chosen at Step 1 by an explicit `--mode`
argument, or by looking at `docs/design/` and confirming with the user
(detection never decides alone; when nothing covers the epic it says `design`
in one line rather than spending a question):

| Phase | Name | Mechanism | `design` | `split` | Output |
|-------|------|-----------|----------|---------|--------|
| 1 | Requirement Understanding | Skill: `understand-requirements` | full interview | reduced | `requirements-report.md` (same shape either way; `Mode` + `Design doc` headers) |
| 2 | Behavior Design | Skill: `design-behavior` | ✓ | — | `docs/design/<slug>.md`, updated index + `docs/prd.md`, any ADR — left **uncommitted** |
| 3 | Task Planning | Skill: `plan-tasks` | ✓ | ✓ | `task-breakdown-plan.md` (topological order, AC, verification method, implementation sketch) |
| — | Confirm Gate | Orchestrator inline (`AskUserQuestion`) | ✓ | ✓ | go/no-go before anything external; any ADR shown in full |
| 4 | Docs PR | Orchestrator inline | `docs/<slug>` | ADR-only, if any | one `docs(...)` commit, PR opened (not merged) |
| 5 | Task Registration | Skill: `register-tasks` | ✓ | ✓ | Map Issue + Task Issues via `gh` CLI |

Phase numbers are kept rather than renumbered per mode, so "Phase 3" means one
thing everywhere — the cost is a table with holes in it. `split` reads a design
doc that already exists and never rewrites it: if the doc is wrong or silent on
behaviour a task would need, `understand-requirements` and `plan-tasks` both
stop and report rather than inventing it into an acceptance criterion, and the
orchestrator offers a `design`-mode rerun against that doc. Before splitting an
unmerged design doc it warns and asks, then puts that PR's URL in the Map Issue
header so whoever picks up a task can see the contract could still move.

Phases 2 and 4 are split on purpose: the design doc has to exist before the
breakdown can be derived from it, but nothing should reach git history before
the confirm gate, since feedback there can send the run back to Phase 2.

**Why a mode here when ADR-0001 rejected one for `light-workflow`:** those two
paths differ in their *invariants*, so a flag would have had to be threaded
through six agents. These two differ only in *which phases run* and share every
artifact contract — the report shape, the breakdown template, the Issue
templates, the Task Graph table `implementation-workflow` parses — so the
branch is confined to the orchestrator plus one step each in
`understand-requirements` and `plan-tasks`. That confinement is the property to
re-check before anyone adds a third mode. ADR-0002 has the full argument; it
narrows ADR-0001 rather than superseding it.

**ADRs are `task-splitter`'s main *why* channel, not a rare one.** It writes
documents, not code, so it has no source comments and no multi-file commit to
fall back on — at planning time the routing collapses to "ADR, or the reasoning
is lost". `design-behavior` Step 5 is a mandatory pass over the doc just
written, asking of each statement whether it was contested; `plan-tasks` Step 5
does the same for forks surfaced while cutting tasks. Task sizing and ordering
stay out of ADRs deliberately — that's a snapshot of one planning session and
belongs in the Map Issue's Notes.

See `plugins/task-splitter/skills/*/reference.md` for the behavior/
implementation boundary, the design-doc-versus-ADR worked examples, the
`split`-mode design-doc reading pass, task-grain heuristics, and the Map/Task
Issue body formats.

---

## implementation-workflow Plugin

Takes a task off a `task-splitter` Map Issue (or a standalone requirement)
through user scrutiny, investigation, planning, human-approved test-first
specification, implementation against frozen tests, review, history cleanup,
and PR. Entry point: `/implementation-workflow:implementation-workflow` (the
orchestrator skill lives at `skills/implementation-workflow/`).

| Phase | Name | Mechanism | Output |
|-------|------|-----------|--------|
| 1 | Requirement Understanding & Task Selection | Skill: `requirement-understanding` | `requirements-report.md`; the user picks the task (always asked, even when one is ready) and approves its content at a scrutiny gate; claims it as `in-progress` only after approval |
| 2 | Issue Refinement *(conditional)* | Skill: `issue-refinement` | on `needs-refinement`: rewritten Task/Map Issues + `docs/design/` updates, shipped as **their own PR**, merged before Phase 3 |
| 3 | Branch Setup | Orchestrator inline | `<type>/<issue#>-<slug>` cut from the freshest default branch; refuses to start on a dirty tree |
| 4 | Codebase Investigation | Agent: `repository-explorer` | `impact-analysis-report.md` |
| 5 | Library Investigation *(conditional)* | Agent: `library-researcher` | `library-usage-report.md` |
| 6 | Implementation Planning | Skill: `implementation-planning` | `implementation-plan.md` + CI readiness finding, posted to the Task Issue (or a new standalone tracking Issue) |
| 7 | Test Authoring | Agent: `test-writer` | automated tests, `docs/manual-tests/<slug>.md`, scaffolding, CI if absent, `test-manifest.json` |
| 8 | Test Review Gate & Freeze | Orchestrator inline | human approves the specification → committed locally as one `test(...)` commit; that SHA is the freeze point |
| 9 | Implementation | Agent: `implementer` | **uncommitted** source changes, `why-notes.md`, any ADR; **cannot modify tests of either kind** — escalates via `test-dispute.md`; runs no `git` |
| 10 | Automated Review | Agent: `code-reviewer` | `review-report.md`; verifies the test freeze mechanically before anything else; loops back to Phase 9 on FAIL, up to 5 attempts |
| 11 | Human Review Gate | Orchestrator inline | `approve` or `request-changes` via `AskUserQuestion`; any ADR is reviewed here too |
| 12 | History Cleanup & Persistence | Agent: `persistence-engineer` | commits the working tree as `test` + implementation commits, finalises this run's draft ADRs, pushes (`--force-with-lease` only after a rewrite), opens/updates the PR, fills the Map Issue row's `PR` cell |
| 13 | Map Issue Update | Orchestrator inline | `map-issue`: flips the row to `done`, closes the Task Issue. `standalone`: closes the tracking Issue Phase 6 created. Phases 9/10 flip the row to `blocked` instead on an unresolved halt (`map-issue` only) |

**Two invariants that shape most of the file contracts.** First, *the
implementation is never committed before Phase 12* — the implementer runs no
`git`, so review loops and send-backs happen against a working tree and there
is no messy history to squash. The cost is that Phase 12 must build the series
from `modified-files.json` and verify it against a `git write-tree` snapshot
(not against `HEAD`, which doesn't contain the work), and must never
`git reset --hard`. Second, *there is no agent conversation resume*: every
`Agent(...)` call is a fresh context, and `test-writer` / `implementer` carry
continuity in `test-authoring-log.md` / `implementation-log.md`, which they
read first and append to last.

Shared premises live in `plugins/implementation-workflow/docs/`, which the
orchestrator resolves once at Step 0 and passes into every agent prompt:

| Doc | Covers |
|-----|--------|
| `vcs-minimalism.md` | what may land in VCS, the *why* routing, ADR rules and the two acceptance paths |
| `git-workflow.md` | branching, commit shape, where the implementation gets committed, the soft-reset regroup, push policy |
| `test-first.md` | the `test-writer`/`implementer` contract, the two kinds of test, how the freeze is verified |
| `map-issue.md` | the Task Graph table and its status vocabulary, which phase writes which cell, and the `gh issue edit --body-file -` whole-body-rewrite pattern |

The first three are read by every file-writing agent; `map-issue.md` is read by
whoever touches a GitHub Issue — the orchestrator, `requirement-understanding`,
`issue-refinement`, and `persistence-engineer`.

See `plugins/implementation-workflow/skills/*/reference.md` and `agents/*.md`
for per-criterion automated/manual routing, the scrutiny checklist, the
review-loop cap, and the PR body contract.

Standalone skill (outside the thirteen-phase pipeline): `onboarding`
(`/implementation-workflow:onboarding`) — verifies `gh` CLI/GitHub-remote
prerequisites, reports CI and `docs/adr/` readiness, and creates or updates the
consuming project's `docs/tool.md`. Run once when adopting the plugin, or
whenever project tooling changes. See
`plugins/implementation-workflow/skills/onboarding/reference.md` for the
manifest-file auto-detection heuristics.

---

## light-workflow Plugin

Takes a requirement straight from a discussion with the user to a PR, without
the gates `implementation-workflow` exists to enforce. One user-invocable
orchestrator skill, no subagents, no sub-skills, no workspace directory. Entry
point: `/light-workflow:light-workflow` (skill at `skills/light-workflow/`).

| Phase | Name | Mechanism | Output |
|-------|------|-----------|--------|
| 0 | Branch Preparation | Orchestrator inline | `<type>/<slug>` cut from the current tip of the default branch — or the current branch reused, if it already contains that tip |
| 1 | Requirement Discussion | Orchestrator inline | a five-point understanding written back and confirmed **in the conversation**; no file |
| 2 | Implementation | Orchestrator inline | **uncommitted** source changes, source comments carrying local *why*, any `draft` ADR, a drafted verification procedure |
| 3 | Approval Gate | Orchestrator inline (`AskUserQuestion`) | `approve` / `request-changes`; uncapped send-back loop to Phase 2 |
| 4 | Commit, Push, PR | Orchestrator inline | ADRs flipped to `accepted`, the commit series, `git push -u`, PR opened (not merged) |

**What it deliberately does not have**, and must not grow back: test code (it
runs the project's existing checks but writes none), a committed verification
procedure, any GitHub Issue interaction, an automated review pass, and any file
under `.claude/`. Its verification procedure lives in the PR body; the reason
that differs from `implementation-workflow`'s committed `docs/manual-tests/` is
that this plugin has no specification freeze, so the procedure is a run-time
artifact rather than a contract. Written up in
`plugins/light-workflow/docs/vcs-minimalism.md` §1 and in ADR-0001.

**What it keeps, unchanged from `implementation-workflow`:** source code as the
only *how* in VCS, the three *why* channels with the same half-day test,
nothing committed before human approval, and a history that is the shape of the
change rather than of the work (Phase 2 runs no `git` beyond reads — the whole
implementation is uncommitted until Phase 4).

The full contract — the discussion question bank, the "stop and ask" test, the
verification-procedure format, the PR body contract, and a divergence table
against `implementation-workflow` — is in
`plugins/light-workflow/skills/light-workflow/reference.md`.

---

## Shared Conventions (all three plugins)

- **No bundled MCP servers.** No plugin ships a `.mcp.json`. GitHub
  operations go through the `gh` CLI. Code search and library-doc lookup
  default to built-in tools (`Grep`/`Glob`/`Read`, `WebSearch`/`WebFetch`).
  Project-specific MCP tools (a code-search server, a docs server, a
  Playwright/Godot MCP for verification, etc.) are declared by the
  *consuming* project in its own `docs/tool.md`; skills/agents `ToolSearch`
  for them by name when `docs/tool.md` mentions one. The `task-splitter` and
  `implementation-workflow` orchestrators check for `docs/tool.md` at startup
  and print a starter template if it's missing — this is a nudge, not a
  requirement. `light-workflow` makes the same check but only mentions the file
  in one line, deliberately: printing the template would mean a third copy of
  `tool-template.md` to keep in sync, for a plugin whose whole premise is less
  ceremony. `implementation-workflow`'s `onboarding` skill is where a user
  actually resolves that nudge instead of dismissing it, whichever plugin
  raised it.
- **No custom session-management infrastructure.** No SessionStart hooks, no
  `status.json` state machine. Cross-phase handoff is plain markdown files
  under `.claude/task-splitter/<task-id>/` or
  `.claude/implementation-workflow/<task-id>/`. Orchestrators use the
  harness's own `TaskCreate`/`TaskUpdate` for in-session progress tracking.
  Agents are likewise never "resumed": each invocation is a fresh context that
  reads its own append-only log from the task directory. If a session is
  interrupted, resuming is manual: tell the orchestrator which task directory
  to continue, and it infers what's done from which files already exist there —
  with the one exception that uncommitted implementation work does not survive
  a restart. `light-workflow` takes this further and keeps **no** files at all:
  it runs inline in one conversation, so after a restart only the branch and
  the working tree remain, and it re-confirms the requirement rather than
  inferring it.
- **VCS minimalism.** The *how* is carried by source code alone — plans,
  reports, review findings, and implementation narrative go to Issues and PR
  bodies, never to a committed file. The *why* always goes into VCS, in
  one of three places: a source comment (reasoning local to one file), the
  commit message body (reasoning spanning several), or an ADR (any decision a
  human would need half a day or more to reverse). Each plugin carries its own
  copy of this policy at `plugins/<plugin>/docs/vcs-minimalism.md` because
  plugins install independently — there are now **three** copies, so
  **change one, change all three.** The *why* routing and the ADR rules are the
  same policy in all three and must stay that way — they are §2 and §3 in
  `implementation-workflow` and `light-workflow`, and §3 and §4 in
  `task-splitter`, which carries an extra planning-time artifact-routing table
  as its §2. The one sanctioned divergence is in `light-workflow`'s §1, where
  the verification procedure goes to the PR body instead of
  `docs/manual-tests/`, and it is marked as a divergence in the file itself.
  Each copy may also *append* material specific to its own plugin — the
  planning-time ADR signals in `task-splitter`'s §3, the two-mode ADR carrier
  table in its §6 — as long as the shared text stays equivalent.
- **Four cross-plugin duplications exist on purpose**, because a plugin has to
  work with the others absent and so cannot link into them: the three
  `docs/vcs-minimalism.md` copies, the two `templates/tool-template.md` copies
  (`light-workflow` deliberately has none), the Map Issue table contract
  (`task-splitter`'s `map-issue-template.md` ↔ `implementation-workflow`'s
  `docs/map-issue.md`), and the three `docs/sandbox-environment.md` copies
  documenting the sandboxed environment every file-writing or network-calling
  agent/skill runs in — what's readable, what's writable, which hosts are
  reachable directly vs. only through `WebFetch`/`WebSearch`, and why a push
  must always name its branch explicitly instead of using `-u`. Only §6 ("Who
  reads this") differs between those three, because each plugin has a different
  set of readers. Keep the existing copies in sync by hand. Duplication
  *within* a plugin is not in this category — extract it into that plugin's
  `docs/` and link to it. If a fifth workflow ever needs a fifth policy copy,
  revisit the arrangement instead (ADR-0001's last consequence).
- **`docs/adr/`** holds numbered ADRs (`NNNN-<slug>.md`, sections Status /
  Context / Decision / Consequences / Alternatives Considered) plus
  `docs/adr/index.md`, updated in the same commit as the ADR it describes.
  Lifecycle: written as `draft`, flipped to `accepted` when the change ships;
  once out of `draft`, `Decision` and `Context` are immutable and a change of
  mind means a new superseding ADR. **Two acceptance paths:** an ADR from
  `implementer` (Phase 9) is flipped by `persistence-engineer` at Phase 12
  after the review gate — and only ADRs from *this run*, never someone else's
  draft. An ADR from `issue-refinement` (Phase 2) is written `accepted`
  directly, because its doc PR *is* the change that ships the decision and has
  no later gate; the same holds for a `task-splitter` Phase 4 ADR, in either
  mode — `design` ships it inside the design-doc PR, `split` opens an ADR-only
  PR for it since no document changed and there is nothing else to ride on. A
  `light-workflow` ADR follows the first path in miniature: written `draft` in
  its Phase 2, flipped to `accepted` in its Phase 4 after the approval gate, by
  the orchestrator itself and only for ADRs that run wrote.
  `docs/decision-records/` and `docs/incident-logs/` are frozen historical
  reference; no new entries.
- **`docs/manual-tests/`** holds one committed procedure per feature area
  (`<slug>.md`), indexed by `docs/manual-tests/index.md`, which the consuming
  project's `README.md` links to. An automated test is an executable statement
  of behaviour; a manual test is a non-executable one, for behaviour a runner
  can't check. Both are *what*, not *how*, so both are committed; both are
  frozen in the same `test(...)` commit at Phase 8; the implementer may edit
  neither. The **record of one execution** is not committed — that's a run log
  and goes to the PR body and the Issue. There is therefore **always** a test
  commit, including for a task whose specification is entirely manual. All of
  this is `implementation-workflow`'s; `light-workflow` writes neither kind of
  test and hands its verification procedure to the PR body instead.
- **`docs/design/`** holds one behavior-only doc per feature — observable
  inputs/outputs, interfaces, constraints, state transitions. No language,
  library, algorithm, or file-layout detail. **No `## Implementation Notes`
  section** — that was a *how* document in VCS and has been removed; technical
  decisions now route to the three *why* channels above, and implementation
  narrative to the PR body.
- **`docs/prd.md`** is a single living file: product goals, scope boundaries,
  and links into `docs/design/`. Updated incrementally by `task-splitter`,
  never overwritten wholesale.
- **No tool allowlists.** No plugin's skills declare `allowed-tools` and no
  agent carries a "Tool Discipline" section — all three assume a sandboxed
  environment. Restrictions that are *behavioural* rather than
  mechanical are still stated as rules (the implementer not touching frozen
  tests, investigation agents not editing source).
- **Markdown link integrity is CI-enforced.** `.github/workflows/markdown-link-check.yml`
  runs `lychee` (config: `lychee.toml`) on any push/PR touching a `*.md` file,
  so a broken relative reference between `SKILL.md`/`reference.md`/templates,
  or into `docs/`, fails the build. Skills and agents that link to sibling
  docs don't need to manually re-verify those references stay valid.
- **Relative markdown links in a skill's own body resolve correctly — this was
  verified empirically, not assumed.** On every `Skill(...)` invocation the
  harness prefixes the loaded body with `Base directory for this skill:
  <absolute path>`; the model joins that with the body's relative links
  (`[reference.md](reference.md)`, `[../../docs/map-issue.md](...)`) to `Read`
  them. Confirmed by installing an official marketplace plugin
  (`claude-code-setup`) and observing its `references/*.md` links resolve from
  its own (non-cwd) skill directory. `${CLAUDE_PLUGIN_ROOT}` is a different,
  narrower mechanism for a different problem: a path a **Bash command** or
  **subagent prompt** needs, where the shell's cwd is the user's project root
  and knows nothing about "base directory for this skill". Do not convert this
  plugin's skill-body relative links to `${CLAUDE_PLUGIN_ROOT}` — that would
  break `lychee` for no correctness gain.
- Subagent return values are chosen per phase for what's actually useful to
  the caller — not a fixed "summary only" rule.
