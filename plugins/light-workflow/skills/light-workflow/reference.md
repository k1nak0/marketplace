# Light Workflow — Extended Reference

Sections are referenced by number from [SKILL.md](SKILL.md).

## 1. Running the Requirement Discussion (Phase 1)

The user has a requirement in their head and a sentence of it in the prompt.
Your job is to get the rest of it out, in as few questions as it takes.

### Before the first question

Ground yourself in the repository, or every question you ask will be one the
user has to answer twice — once for you, once for the code:

- `Grep` the feature name, the main symbols, the user-facing strings.
- `Read` the files that would plausibly change.
- Look for a `docs/design/<slug>.md` covering this area, and for an existing
  implementation the requirement seems unaware of.
- Note the project's conventions for the kind of thing you're about to write —
  error handling, naming, where this kind of code lives.

Then open the discussion with what you found: *"There's already a `SessionStore`
doing X in `store.ts:40` — is this meant to replace it or sit alongside it?"* is
one question that resolves five.

### The question bank

Ask in small batches, not one at a time and not all at once. Stop as soon as
the five points in SKILL.md's Phase 1 are answerable — this is a discussion,
not an intake form.

**Observable behaviour**
- What does a user (or caller, or operator) do, and what should happen?
- What should happen when it goes wrong — which errors are expected, and what
  does the user see?
- Is there a case at the edge of this that you want handled the same way?

**Scope**
- Is <the adjacent thing I noticed> part of this, or a separate change?
- Is this the whole change, or the first step of something larger?

**Done-ness**
- What would you check, by hand, before believing this works?
- Is there a specific case that would make you say it's *not* done?

**Constraints**
- Does anything currently depend on the behaviour we're changing?
- Is a new dependency acceptable here, or should this use what's already in the
  project?
- Anything about performance, compatibility, or security this has to respect?

**Non-regression**
- What must keep working exactly as it does now?

### Asking well

- **Two interpretations beat one open question.** "Should the cache be
  invalidated on write, or on read when stale?" with the trade-off in each
  description gets a decision; "how should caching work?" gets a paragraph you
  still have to interpret.
- **Lead with a recommendation** when you have one, as the first option.
- **Name a decision as a decision.** If an answer will still be shaping the
  code in six months, say so in the question — the user answers differently
  when they know it's a fork, and you'll need the rationale in Phase 2 anyway.
- **Don't ask what the code answers.** Reading a file is free; a question is
  not.

### Writing the understanding back

Close with a block short enough to correct in one line:

```markdown
**Building:** <one sentence — what changes, observed from outside>
**Not building:** <the out-of-scope list>
**Done when:** <checkable conditions, one line each>
**Constraints:** <what binds the implementation>
**Must not change:** <existing behaviour that has to keep working>
**Branch:** <type>/<slug>
```

If the user corrects it, amend and show it again. This is the thing Phase 3
compares the result against.

## 2. When to Stop and Ask (Phase 2)

The instruction is "consult the user when you get stuck", and the failure modes
run in both directions: an agent that asks about everything is exhausting, and
an agent that decides everything silently is the reason the approval gate hurts.

**Ask when:**

| Situation | Why it's worth an interruption |
|---|---|
| A real fork with materially different consequences (a data shape, an interface, a dependency, an error contract) | The user is the one who lives with it, and it's cheap now |
| The requirement contradicts what the code actually does | One of the two is wrong and you can't tell which |
| A requirement nobody stated — the change can't be finished without answering something Phase 1 didn't cover | Guessing here is how scope creep starts |
| The clean fix is outside the agreed scope | Widening scope is the user's call, never yours |
| Something in the repo is already broken, unrelated to this change | They may want it fixed, filed, or left alone |
| A new dependency, if Phase 1 didn't already settle it | Dependencies are hard to remove later |

**Don't ask when:**

- The answer is in the codebase, the docs, or `docs/tool.md`. Read it.
- It's a matter of taste with an obvious local convention. Follow the
  convention.
- It's reversible in five minutes and you can explain the choice at Phase 3.
  Choose, note it, move on.
- You're asking for reassurance rather than a decision. "Shall I continue?" is
  not a question.

**How to ask:** `AskUserQuestion`, your recommendation first, and the *actual*
trade-off in each option's description — not a restatement of the option label.
If the answer is a decision with a lifetime, route its *why* immediately
(comment / commit message / ADR) rather than trusting yourself to remember it
at Phase 4.

## 3. The PR Body Contract (Phase 4)

Everything a reviewer needs that is not in the diff lives here — this is the
only durable home for it, and it is never expected to stay current.

```markdown
## Summary

<What changes, observed from outside. Two or three sentences. The requirement
as agreed at Phase 1, not a narration of the files touched.>

## Why

<The reasoning a reviewer needs to judge the change. For decisions recorded
elsewhere, link rather than restate: "Optimistic locking over row locks — see
ADR-0007." Decisions whose rationale is in a commit body can be summarised in
one line each.>

## Manual Verification

<The numbered procedure from §4, verbatim. This is the durable copy — the
plugin commits no verification file.>

## Checks Run

<Build / lint / existing test suite, with the command and its result. Say so
plainly if something was skipped or failed, and why.>

## Out of Scope

<What was deliberately not done, and anything noticed on the way that someone
should look at later — an out-of-date design doc, a pre-existing bug.>
```

Omit a section only when it would be genuinely empty — an absent
`## Checks Run` says the project has no checks, and an empty `## Out of Scope`
says you looked and found nothing. Both are information; a missing section that
should have had content is not.

This plugin creates no Issue. If the user pointed at an existing one, add a
`Refs: #N` line at the end of the body and leave the Issue alone — no claiming,
no closing, no status table.

## 4. The Verification Procedure (Phases 2–4)

This plugin writes no test code, so this procedure is the entire verification
story. Write it for a person who has the branch checked out and has not read
the diff.

```markdown
### Verification

**Setup:** <what to run/check first — build, migrate, seed, a specific state>

1. **<Action>** — <exactly what to do, with the concrete input>
   → **Expect:** <the observable result, specific enough to be wrong>
2. **<Action>** — …
   → **Expect:** …

**Also check nothing regressed:** <the one or two existing behaviours nearest
the change, from Phase 1's "must not change">
```

Rules that make the difference between a procedure and a gesture:

- **Concrete inputs.** "Search for `ana`" beats "search for something".
- **Expected results that can fail.** "Returns 409 with an `existing_id`
  field" is checkable; "behaves correctly" is not.
- **Cover the failure paths**, not just the happy one. The bugs live there.
- **Include the non-regression check** from Phase 1 — the most common damage
  from a small change is to its neighbours.
- **Say what you already ran yourself.** If you executed a step and saw the
  expected result, mark it and give the output; don't make the user redo it
  blind.

Worked example:

```markdown
### Verification

**Setup:** `npm run dev`, logged in as any user.

1. **Search for a user by partial name** — type `ana` in the member search box.
   → **Expect:** `Ana Ruiz` and `Hanan Sato` both appear within ~1s; the match
   is case-insensitive and matches anywhere in the name.
2. **Search for something with no match** — type `zzzz`.
   → **Expect:** the empty state "No members found", not a spinner and not an
   error toast.
3. **Search while offline** — dev tools → Network → Offline, type `ana`.
   → **Expect:** the inline message "Couldn't reach the server", previous
   results left on screen. (Ran this one — see output in Checks Run.)

**Also check nothing regressed:** the member list still paginates at 50 with an
empty search box.
```

## 5. Commits (Phase 4)

```
<type>(<scope>): <summary — imperative mood, ≤72 chars, no trailing period>

<Body. Present tense. This is one of the three places the *why* lives — see
../../docs/vcs-minimalism.md §2. Include the rationale for any decision that
spans more than one file in this commit and isn't heavy enough for an ADR. Do
not narrate the *how*: the diff already says what changed.>

Refs: ADR-NNNN   <- when this commit implements a recorded decision
```

Types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`.

- **Staging is explicit** — `git add -- <paths>`, never `git add -A` or
  `git add .`. Nothing under `.claude/` is ever staged.
- **Split by meaning, not by chronology.** Several commits are welcome when the
  parts are genuinely separable and each one builds; "wip", "fix review
  comment", and "revert previous" are never commits, because the work stayed
  uncommitted until the user approved it.
- **An ADR ships in the commit it justifies**, already flipped to `accepted`,
  together with its `docs/adr/index.md` row.

The resulting series is what the reviewer sees:

```
$ git log --oneline <base>..HEAD
<type>(<scope>): <summary>      ← one, or a few split by meaning
```

## 6. Divergences from `implementation-workflow`

Reach for the heavier plugin when a run keeps bumping into the right-hand
column.

| | `light-workflow` | `implementation-workflow` |
|---|---|---|
| Phases | 5, all inline | 13, most in isolated agents |
| Requirement source | a discussion with the user | a Map Issue task or a standalone requirement, scrutinised at its own gate |
| Tests | none written; existing checks are run | a separate agent writes them, the user approves them, they're frozen in a commit before implementation |
| Verification procedure | PR body only | committed to `docs/manual-tests/<slug>.md`, indexed, re-runnable |
| Review | the user, once, at Phase 3 | a fresh-context `code-reviewer` that verifies the freeze, then the user |
| Send-backs | user's word, no cap | capped at 5 automated fix rounds, then `blocked` |
| GitHub Issues | none created, claimed, or closed | tracking Issue, Map Issue row, status lifecycle |
| Handoff files | none | `.claude/implementation-workflow/<task-id>/` |
| Survives a session restart | only the branch and the working tree | every phase's output, plus the frozen test commit |
| *Why* in VCS | identical | identical |
| *How* outside source code | identical — never | identical — never |
| Implementation committed before approval | never | never |

The last three rows are the point: the gates are what got lighter, not the
rules about what ends up in the repository.
