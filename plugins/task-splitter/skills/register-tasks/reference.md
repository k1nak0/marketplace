# Register Tasks — Extended Reference

## Why Four Steps Instead of One

Task Issue bodies cross-reference the Map Issue number and each other's issue
numbers (`Depends on: #123`). Those numbers don't exist until the issues are
created, so creation and body-filling have to be separate passes:

1. Create Map Issue (empty) → get its number
2. Create Task Issues (empty) → get their numbers
3. Fill Map Issue body (needs all Task Issue numbers)
4. Fill Task Issue bodies (needs Map Issue number + dependency issue numbers)

## `issue-map.json` Shape

```json
{
  "map_issue": 100,
  "tasks": [
    {"title": "Add X", "issue": 101, "depends_on": []},
    {"title": "Add Y", "issue": 102, "depends_on": [101]}
  ]
}
```

Write it after every single `gh issue create`/`gh issue edit` call — not just
at phase boundaries. If this skill is re-invoked and finds a populated
`issue-map.json`, resume from the first step that has a `null` issue number
(Step 2) or, if all issues exist but bodies still look like the placeholder
text ("Registering — filled in shortly."), resume from Step 3.

## Labels

`gh issue create --label` requires the labels to already exist in the target
repo, or it will error. If label creation fails, retry without `--label`
rather than blocking the whole registration on it — labels are a nice-to-have,
not a correctness requirement.

## Body Escaping

Pass Issue bodies to `gh issue create`/`gh issue edit` via `--body-file -`
with a heredoc, not `--body "<inline string>"`, to avoid shell-escaping
problems with markdown tables and code fences:

```bash
gh issue edit <number> --body-file - <<'ISSUE_BODY'
<full markdown body>
ISSUE_BODY
```
