# Git Workflow — Branches, Commits, and History

Shared policy. Any agent or skill in this plugin that runs `git` or `gh`
follows it. It exists so that what reaches the default branch is the *shape of
the change*, never the *shape of the work that produced it*.

---

## 1. Branches

**Nothing in this pipeline ever commits to the default branch.** A work branch
is cut in Phase 3, immediately after the task is confirmed, and every commit
this run produces lands on it.

```bash
BASE=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
git fetch origin "$BASE"
git switch --create "<type>/<issue#>-<slug>" "origin/$BASE"
```

**Naming:** `<type>/<issue#>-<slug>`

- `<type>` — the Conventional Commits type the change will land as: `feat`,
  `fix`, `refactor`, `perf`, `docs`, `test`, `chore`.
- `<issue#>` — the tracking Issue number, no `#`.
- `<slug>` — 3–5 kebab-case words from the Issue title.

`feat/124-add-user-search`, `fix/301-null-session-on-logout`.

For a `standalone` run the Issue is created in Phase 6 before any commit
exists, so the same rule applies — the branch is cut in Phase 3 with a
placeholder-free name derived from the requirement, and renamed once the Issue
number is known if it isn't yet.

**Before cutting the branch**, verify the working tree is clean:

```bash
git status --porcelain -- . ':!.claude'   # must be empty
```

If it isn't, stop and surface it — do not stash, commit, or discard someone
else's work in progress.

Exclude `.claude` from every cleanliness check. The run's own scratch workspace
lives under `.claude/implementation-workflow/<task-id>/` and is untracked in
any project that doesn't gitignore `.claude/`; a bare `git status --porcelain`
would report the pipeline's own handoff files as a dirty tree.

### The design-doc branch is separate

When Phase 2 (`issue-refinement`) revises Issues and design docs, those changes
go out as their **own** branch and PR (`docs/<issue#>-<slug>`), and the run
waits for that PR to be merged before Phase 3 cuts the implementation branch
from the updated default branch. Design-doc churn never appears in the
implementation PR's diff.

## 2. The shape of a finished PR

A PR from this pipeline reaches the reviewer as:

```
<type>(<scope>): <implementation summary>      ← one or more, split by meaning
test(<scope>): <what behaviour is now specified>   ← always exactly one, first
```

- **The test commit is first and is exactly one commit.** It contains the test
  files, any signature-only scaffolding they need to compile, and — if the
  project had no CI able to run them — the CI configuration that now does.
- **The implementation commits follow.** One is fine; splitting into several is
  encouraged when the change has genuinely separable parts (each commit
  building and passing on its own). Never split them along the lines of *when
  you did the work*.
- Nothing else. No "fix review comment", no "wip", no "revert previous", no
  merge commits from the base branch.

## 3. Commit messages

```
<type>(<scope>): <summary — imperative mood, ≤72 chars, no trailing period>

<Body. Present tense. This is one of the three places the *why* lives — see
vcs-minimalism.md. Include the rationale for any decision that spans more than
one file in this commit and isn't heavy enough to warrant an ADR. Do not
narrate the *how*: the diff already says what changed.>

Refs: ADR-NNNN            <- when this commit implements a recorded decision
Closes #<tracking-issue>  <- on the last commit of the series only
```

Types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`.

Staging is always explicit — `git add -- <paths>`, never `git add -A` or
`git add .`. Nothing under `.claude/` is ever staged.

## 4. Rewriting history before you push

Work does not proceed in a straight line: automated review sends the
implementation back, the human gate sends it back, and sometimes a problem is
only visible once everything is assembled. **All of that is expected — it just
doesn't get to be part of the history.** Let the work be messy locally, then
regroup before it becomes visible.

**The invariant: `git log <base>..HEAD` matches §2 at the moment of every
push.** Not before, not after — every push.

### Regrouping

Before pushing, record a recovery point and rebuild the series from the diff:

```bash
git rev-parse HEAD > .claude/implementation-workflow/<task-id>/pre-rewrite-sha
BASE_SHA=$(git merge-base HEAD "origin/$BASE")

git reset --soft "$BASE_SHA"   # every change is now staged; nothing is lost
git restore --staged .         # unstage, keeping the working tree untouched

# then, once per commit in the target series:
git add -- <paths belonging to this commit>
git commit -m "..."
```

The first commit built this way is the test commit (test files, scaffolding,
CI config); the rest are the implementation commits, split by meaning. The
tree at `HEAD` after the last commit must be byte-identical to the tree before
the rewrite — verify it:

```bash
test -z "$(git diff $(cat .claude/implementation-workflow/<task-id>/pre-rewrite-sha) HEAD)" \
  && echo "tree preserved" || echo "REWRITE CHANGED THE TREE — abort"
```

If that check fails, reset back to the recorded SHA
(`git reset --hard $(cat …/pre-rewrite-sha)`) and report the problem rather
than pushing something you can't account for.

Never use `git rebase -i` — interactive rebase isn't available in this
environment. The soft-reset regroup above needs no editor and is deterministic.

### Pushing

```bash
git push -u origin HEAD                    # first push of the branch
git push --force-with-lease origin HEAD    # after any rewrite of a pushed branch
```

- `--force-with-lease`, never bare `--force`.
- **Only ever force-push the work branch this run created.** Never the default
  branch, never a branch you didn't cut.
- If a push is rejected for a reason other than the lease (auth, protected
  branch, network), surface the error and stop. Do not retry with `--force`.

## 5. Where the test commit sits in time

The test commit is created the moment the human approves the tests — it is a
**local commit only**. Nothing is pushed until the whole change has cleared
the human review gate and the history has been regrouped. That keeps the
approved tests safe from being lost to a later rewrite (they're in the reflog
and in the recorded recovery SHA) without publishing a branch that will need
rewriting three times before anyone should look at it.

Once the PR is open and the reviewer sends the change back, the same regroup
applies, followed by `--force-with-lease`.
