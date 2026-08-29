# Test-First — The Contract Between `test-writer`, `test-reviewer`, and `implementer`

Shared policy for Phases 7–12.

**This is test-first, not TDD.** The difference is not cosmetic:

| | TDD | Test-first (this plugin) |
|---|---|---|
| Who writes the tests | The implementer | A separate agent, `test-writer` |
| When they're approved | Never explicitly | By a human, before any implementation exists |
| When they're committed | Alongside the implementation | Before implementation starts, as their own commit |
| Can the implementer change them | Yes, freely, as the design emerges | **No** |

What is unchanged from TDD: **the tests are the specification of the
behaviour.** A test asserts what the system does as observed from outside it,
in the vocabulary of the requirement — not what the implementation happens to
do internally.

The point of the split is that a specification approved by a human, and frozen
before the implementation exists, cannot be quietly bent to match whatever got
built.

---

## Two kinds of test, one specification

A task's specification has two halves, and most tasks have both:

| | Automated tests | Manual tests |
|---|---|---|
| What it is | An **executable** document | A **non-executable** document |
| Lives in | The project's test suite | `docs/manual-tests/<slug>.md` |
| Checked by | The test runner, in CI | A human, following the steps |
| Committed? | **Yes** | **Yes** |
| Frozen after Phase 9? | **Yes** | **Yes** |

That is the *only* difference between them. Both state observable behaviour in
the requirement's vocabulary, both are read by a human at the Phase 9 gate,
both go into the same `test(...)` commit, and the implementer may edit neither.

**There is always a test commit.** Even a task whose behaviour is entirely
visual produces one — it carries the manual-test document.

Automated is the default and the strong preference: an executable document
cannot silently rot. A behaviour becomes a manual test only when an automated
test genuinely cannot express it — a rendered surface, a live external system.
"Awkward to test" and "the suite has no precedent for this" are reasons to
write the fixture, not reasons to write a manual test.

### Where manual tests live

`docs/manual-tests/<slug>.md`, one file per feature area, indexed by
`docs/manual-tests/index.md`, which the project's `README.md` links to. They
are reachable documentation, not a scratch artifact: the whole reason they are
committed rather than posted to an Issue is that someone has to find and re-run
them before the *next* release, not just this one.

The **procedure** is what's committed there — never the record of one
execution. See "Executing the manual tests" below.

---

## The sequence

```
Phase 7   test-writer writes the automated tests and the manual-test doc.
          No production code.
          Runs the automated ones → they must fail, for the right reason.
Phase 8   test-reviewer reviews the candidate — fresh eyes, before any human
          sees it.
          ├── FAIL → back to test-writer (capped, automatic)
          └── PASS → Phase 9
Phase 9   Human reads both, plus test-reviewer's report, and approves them.
          ├── request-changes → back to Phase 7 (through Phase 8 again)
          └── approve → commit them  (test(...): …, local only)   ← FREEZE POINT
Phase 10  implementer makes the automated tests pass and executes the manual
          steps. Both documents are now immutable.
Phase 11  code-reviewer verifies neither was touched.
```

## What `test-writer` may write

- **Test files.** The behaviour under test, expressed as assertions a human can
  read as a specification.
- **The manual-test document** under `docs/manual-tests/`, plus its row in
  `docs/manual-tests/index.md` and — if absent — the `README.md` link to that
  index.
- **Scaffolding, only where a language demands it.** In a compiled or
  statically-checked language the test won't build unless the symbols it calls
  exist. `test-writer` may create the *minimum* signature-only declarations
  needed to compile — an empty function with the right signature whose body
  raises/returns a "not implemented" error, nothing more. No logic, no partial
  implementation.
- **CI configuration, when the project has none that can run these tests.** If
  there are automated tests, they must actually run somewhere other than one
  agent's laptop. If no CI workflow exists, or the existing one doesn't execute
  this suite, `test-writer` adds or extends it as part of the same commit.

`test-writer` writes **no production code**. If it finds itself needing to, the
scaffolding rule above is the ceiling — anything more means the task is
underspecified, and it should halt and say so rather than start implementing.

## What `test-reviewer` checks (Phase 8)

Before any human sees the candidate specification, a fresh-context agent
reviews it against everything above: that the automated tests fail for the
right reason, that every acceptance criterion is covered and correctly
bucketed, that assertions are observable and discriminating rather than
tautological or internals-coupled, that manual steps carry a concrete pass
criterion and an honest reason they aren't automated, that scaffolding stays
within the signature-only ceiling, and that CI actually runs the suite. A FAIL
sends the candidate back to `test-writer`, automatically, up to five times,
before it ever reaches the Phase 9 human gate — see `agents/test-reviewer.md`
for the full checklist and severity rubric.

This does not make the human gate redundant: `test-reviewer` catches whether
the specification is *internally sound*; the human is the only one who can
judge whether it's the *right* specification for the requirement.

## What `implementer` may not do

After the freeze point, the following are all forbidden, without exception:

- Editing, deleting, renaming, or moving any file in `test_files` or
  `manual_test_files`.
- Weakening a test: relaxing an assertion, widening a tolerance, adding
  `skip` / `xfail` / `.only` / `pending`, commenting a case out. For a manual
  step: softening its pass criterion, or reinterpreting it as satisfied.
- Changing the test runner's configuration, fixtures, or CI workflow so that a
  frozen test stops running, stops failing the build, or runs against different
  inputs.
- "Fixing" a test that it believes is wrong.

The scaffolding files are **not** frozen — replacing those stubs with real
implementations is precisely the implementer's job.

## When the implementer believes a test is wrong

This happens, and it is not a failure of the process — it usually means the
specification had a genuine gap that only became visible under
implementation. The implementer's move is to **stop and escalate, never to
edit.** This applies identically to an automated test and to a manual step.

Write `.claude/implementation-workflow/<task-id>/test-dispute.md`:

```markdown
# Test Dispute

**Task ID:** <task-id>
**Test(s) in question:** <test id / name / file:line, or manual step number>

## What the test asserts
## Why I believe it's wrong
<A wrong expected value? An assertion about an unspecified detail? A
contradiction with another test or with the Issue? Be specific — "it's hard to
make pass" is not a dispute, it's a difficulty.>

## What I believe it should assert instead
## What I've already tried
```

Then halt and return. The orchestrator surfaces it to the human, who either
sends the run back to Phase 7 to amend and re-approve the specification (the
test commit is amended, not appended to), or rejects the dispute and the
implementer resumes under the original specification.

## The manifest

`test-writer` records the contract in
`.claude/implementation-workflow/<task-id>/test-manifest.json`:

```json
{
  "test_commit": null,
  "test_files": ["path/to/test_a"],
  "manual_test_files": ["docs/manual-tests/booking.md"],
  "scaffold_files": ["path/to/stub"],
  "ci_files": [".github/workflows/test.yml"],
  "test_command": "<command that runs the suite>"
}
```

- Either `test_files` or `manual_test_files` may be empty. **Not both** — a
  task with no specification of either kind has nothing to freeze and nothing
  to review; halt and say so.
- `test_commit` stays `null` until the orchestrator fills it in at the freeze
  point.
- `test_command` may be `null` when `test_files` is empty.

## How the freeze is verified (Phase 11)

`code-reviewer` checks, mechanically, before reviewing anything else:

```bash
# no committed change since the freeze
git diff --stat <test_commit>..HEAD -- <test_files> <manual_test_files>   # must be empty
# no uncommitted change either — the implementation is uncommitted at this point,
# so this is the check that actually catches tampering
git status --porcelain -- <test_files> <manual_test_files>                # must be empty
git diff <test_commit>..HEAD -- <ci_files>                                # inspect any change
git status --porcelain -- <ci_files>                                      # inspect any change
```

Any change to `test_files` or `manual_test_files` is a **Critical** finding on
its own, whatever the change was and however reasonable it looks. A change to
`ci_files` is not automatically a finding, but any change that reduces what
runs or what fails the build is Critical. `code-reviewer` also re-reads the
frozen specification against the Issue's acceptance criteria: a test that
passes because it asserts nothing meaningful is a Critical finding against the
implementation, not a request to change the test.

## Executing the manual tests

The implementer executes every step in `manual_test_files` **verbatim** and
records the observed result for each. If an observation doesn't match its pass
criterion, that's a failure — fix the implementation, don't reinterpret the
step. The record goes to `why-notes.md` under `## For the PR body`, and from
there into the PR body and an Issue comment. It is never written back into the
committed document.
