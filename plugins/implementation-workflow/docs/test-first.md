# Test-First — The Contract Between `test-writer` and `implementer`

Shared policy for Phases 7–11.

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

## The sequence

```
Phase 7   test-writer writes tests. No production code.
          Runs them → they must fail, for the right reason.
Phase 8   Human reads the tests and approves them.
          ├── request-changes → back to Phase 7
          └── approve → commit them  (test(...): …, local only)   ← FREEZE POINT
Phase 9   implementer makes them pass. Tests are now immutable.
Phase 10  code-reviewer verifies the tests were not touched.
```

## What `test-writer` may write

- **Test files.** The behaviour under test, expressed as assertions a human can
  read as a specification.
- **Scaffolding, only where a language demands it.** In a compiled or
  statically-checked language the test won't build unless the symbols it calls
  exist. `test-writer` may create the *minimum* signature-only declarations
  needed to compile — an empty function with the right signature whose body
  raises/returns a "not implemented" error, nothing more. No logic, no partial
  implementation.
- **CI configuration, when the project has none that can run these tests.** If
  the test strategy is `automated`, the tests must actually run somewhere other
  than one agent's laptop. If no CI workflow exists, or the existing one
  doesn't execute this suite, `test-writer` adds or extends it as part of the
  same commit.

`test-writer` writes **no production code**. If it finds itself needing to, the
scaffolding rule above is the ceiling — anything more means the task is
underspecified, and it should halt and say so rather than start implementing.

## What `implementer` may not do

After the freeze point, the following are all forbidden, without exception:

- Editing, deleting, renaming, or moving any file in `test_files`.
- Weakening a test: relaxing an assertion, widening a tolerance, adding
  `skip` / `xfail` / `.only` / `pending`, commenting a case out.
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
edit.**

Write `.claude/implementation-workflow/<task-id>/test-dispute.md`:

```markdown
# Test Dispute

**Task ID:** <task-id>
**Test(s) in question:** <test id / name / file:line>

## What the test asserts
## Why I believe it's wrong
<A wrong expected value? An assertion about an unspecified detail? A
contradiction with another test or with the Issue? Be specific — "it's hard to
make pass" is not a dispute, it's a difficulty.>

## What I believe it should assert instead
## What I've already tried
```

Then halt and return. The orchestrator surfaces it to the human, who either
sends the run back to Phase 7 to amend and re-approve the tests (the test
commit is amended, not appended to), or rejects the dispute and the
implementer resumes under the original specification.

## How the freeze is verified (Phase 10)

`test-writer` records the contract in
`.claude/implementation-workflow/<task-id>/test-manifest.json`:

```json
{
  "test_commit": "<sha, filled in at the freeze point>",
  "test_files": ["path/to/test_a", "..."],
  "scaffold_files": ["path/to/stub", "..."],
  "ci_files": [".github/workflows/test.yml"],
  "test_command": "<command that runs the suite>"
}
```

`code-reviewer` checks, mechanically, before reviewing anything else:

```bash
git diff --stat <test_commit>..HEAD -- <every path in test_files>   # must be empty
git diff <test_commit>..HEAD -- <every path in ci_files>            # inspect any change
```

A non-empty diff on `test_files` is a **Critical** finding on its own, whatever
the change was and however reasonable it looks. A change to `ci_files` is not
automatically a finding, but any change that reduces what runs or what fails
the build is Critical. `code-reviewer` also re-reads the frozen tests against
the Issue's acceptance criteria: a test that passes because it asserts nothing
meaningful is a Critical finding against the implementation, not a request to
change the test.

## Manual verification strategy

When the plan's strategy is `manual` (UI, live external systems — cases where
an automated test genuinely can't express the behaviour), the same shape
applies with the artifact swapped:

- `test-writer` writes a **verification procedure** — numbered steps, each with
  what to do and the exact observation that constitutes a pass — instead of
  test code.
- The human approves the procedure at the Phase 8 gate.
- The procedure is **not committed**: it's *how* to check, which belongs to the
  Issue and the PR (see `vcs-minimalism.md`). It's posted as an Issue comment
  at approval time. There is no test commit in this case, and the PR consists
  of the implementation commits alone.
- The implementer executes the procedure verbatim and records each step's
  observed result, which goes into the PR body.
- The implementer may not amend the procedure. The dispute path above applies
  unchanged.

If the strategy is `automated`, there is no discretion: the tests are written,
approved, committed, and frozen.
