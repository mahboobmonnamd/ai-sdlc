# Project status snapshot contract

Fetch **all pages** from current GitHub milestone issues and PRs and the authoritative implementation plan. Normalize into a JSON file for `scripts/render_dashboard.py`.

```json
{
  "project": "Example project",
  "snapshot_at": "2026-10-08T10:00:00Z",
  "plan": {
    "source": "https://github.com/org/repo/blob/main/docs/plan.md",
    "revision": "plan-r7",
    "items": [{"issue": 42, "title": "Observable outcome", "milestone": "M003"}]
  },
  "issues": [{
    "number": 42, "title": "Observable outcome", "state": "open",
    "html_url": "https://github.com/org/repo/issues/42",
    "milestone": "M003", "labels": ["needs:review"],
    "updated_at": "2026-10-07T12:00:00Z", "blocked_by": [],
    "checks": "success", "verified": false
  }]
}
```

`plan.items` may be absent when plan authority is unavailable; do **not** insert invented items. `verified=true` must mean actual acceptance evidence, not only closed tracker state. Pass `merged_pr` only when the work's linked merge is verified. `blocked_by` uses issue numbers. If `--milestone` is provided, matching uses exact milestone titles. Include issue/project source URLs; strip tokens and secrets.

Render with:

```sh
python3 skills/projectstatus/scripts/render_dashboard.py --data /path/snapshot.json --milestone M003 --output /path/dashboard.html
```

The renderer uses only Python standard library and creates static HTML without external assets. Return the actual file to the user. It cannot fetch GitHub itself; the invoking agent must collect and reconcile an authoritative snapshot first.
