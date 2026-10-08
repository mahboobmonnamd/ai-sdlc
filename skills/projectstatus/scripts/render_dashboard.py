#!/usr/bin/env python3
"""Render a self-contained HTML delivery dashboard from an authoritative JSON snapshot."""
import argparse
import html
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

LABEL_STATES = {
    "needs:implementation": "READY",
    "issue:implementing": "IMPLEMENTING",
    "needs:review": "REVIEW",
    "pr:reviewing": "REVIEWING",
    "needs:processing": "PROCESSING",
    "pr:processing": "PROCESSING",
    "needs:merge": "MERGE READY",
}

def esc(value):
    return html.escape(str(value if value is not None else "Unknown"), quote=True)

def safe_link(url):
    parsed = urlparse(str(url or ""))
    return esc(url) if parsed.scheme in ("https", "http") and parsed.netloc else ""

def label_names(issue):
    return {x.get("name", "") if isinstance(x, dict) else str(x) for x in issue.get("labels", [])}

def milestone_name(item):
    value = item.get("milestone")
    return value.get("title") if isinstance(value, dict) else value

def state(issue, issue_index):
    if issue.get("state") == "closed":
        return "DONE" if issue.get("verified") is True or issue.get("merged_pr") else "CLOSED (unverified)"
    open_blocks = [n for n in issue.get("blocked_by", []) if str(n) not in issue_index or issue_index[str(n)].get("state") != "closed"]
    if open_blocks:
        return "BLOCKED"
    matches = {LABEL_STATES[n] for n in label_names(issue) if n in LABEL_STATES}
    return next(iter(matches)) if len(matches) == 1 else ("AMBIGUOUS" if matches else "UNMAPPED")

def parsed_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None

def link(text, url):
    url = safe_link(url)
    return f'<a href="{url}" rel="noopener noreferrer">{esc(text)}</a>' if url else esc(text)

def render(data, milestone=None, now=None):
    now = now or datetime.now(timezone.utc)
    plan = data.get("plan") or {}
    plan_items = plan.get("items") or []
    issues = data.get("issues") or []
    if milestone:
        plan_items = [p for p in plan_items if milestone_name(p) == milestone]
        issues = [i for i in issues if milestone_name(i) == milestone]
    all_index = {str(i["number"]): i for i in data.get("issues", []) if "number" in i}
    issue_index = {str(i["number"]): i for i in issues if "number" in i}
    plan_by_issue = {str(p.get("issue", p.get("issue_number"))): p for p in plan_items if p.get("issue", p.get("issue_number")) is not None}
    matched = set(plan_by_issue) & set(issue_index)
    missing = set(plan_by_issue) - set(issue_index)
    unplanned = set(issue_index) - set(plan_by_issue)
    states = {n: state(i, all_index) for n, i in issue_index.items()}
    counts = Counter(states.values())
    coverage = round(100 * len(matched) / len(plan_by_issue)) if plan_by_issue else 0
    stale = [n for n,i in issue_index.items() if i.get("state") != "closed" and parsed_date(i.get("updated_at")) and (now - parsed_date(i["updated_at"])).days >= 21]
    check_failures = [n for n,i in issue_index.items() if i.get("checks") in ("failure","failed")]
    plan_source = safe_link(plan.get("url") or plan.get("source"))
    reconciled = bool(plan.get("items") is not None and (plan.get("source") or plan.get("url")))
    reconciled = reconciled and not missing
    risk = "AT RISK" if counts["BLOCKED"] or check_failures or stale else "NO RECORDED BLOCKERS"
    integrity = "COMPLETE" if reconciled else "INCOMPLETE"

    def metric(value, label, detail):
        return f'<section class="metric"><strong>{esc(value)}</strong><span>{esc(label)}</span><small>{esc(detail)}</small></section>'

    cards = "".join([
        metric(len(issue_index), "Scoped issues", "Current tracker snapshot"),
        metric(f"{coverage}%", "Plan coverage", f"{len(matched)}/{len(plan_by_issue)} matched"),
        metric(counts["BLOCKED"], "Blocked issues", "Unresolved dependencies"),
        metric(len(check_failures), "Failed checks", "Known check failures"),
    ])
    rows = []
    for n,i in sorted(issue_index.items(), key=lambda p: (p[1].get("state") == "closed", int(p[0]) if p[0].isdigit() else 0)):
        age = parsed_date(i.get("updated_at"))
        age_text = f"{(now-age).days} days ago" if age else "Unknown"
        planned = "Matched" if n in plan_by_issue else "Unplanned"
        dependencies = ", ".join(f"#{v}" for v in i.get("blocked_by", [])) or "—"
        rows.append(f'<tr><td>{link("#"+n, i.get("html_url") or i.get("url"))}</td><td>{esc(i.get("title",""))}</td><td>{esc(states[n])}</td><td>{planned}</td><td>{esc(dependencies)}</td><td>{esc(age_text)}</td></tr>')
    if not rows:
        rows = ['<tr><td colspan="6">No issues in the selected milestone.</td></tr>']
    gaps = []
    for n in sorted(missing):
        p = plan_by_issue[n]
        gaps.append(f'<li>Plan issue #{esc(n)}: {esc(p.get("title","Untitled"))} — not found in scoped GitHub issues</li>')
    for n in sorted(unplanned):
        gaps.append(f'<li>GitHub issue {link("#"+n, issue_index[n].get("html_url") or issue_index[n].get("url"))} — not mapped to the plan</li>')
    if not plan.get("items") and plan.get("items") != []:
        gaps.append("<li>Authoritative plan items unavailable; plan-to-issue reconciliation cannot be verified</li>")
    if not plan_source:
        gaps.append("<li>Authoritative plan source URL missing</li>")
    gap_html = "".join(gaps) or "<li>No reconciliation gaps detected in the provided snapshot.</li>"
    action_candidates = []
    if counts["BLOCKED"]:
        action_candidates.append("Resolve open dependency blockers before starting dependent issues.")
    if check_failures:
        action_candidates.append("Triage failed required checks on affected candidates.")
    if missing:
        action_candidates.append("Reconcile missing plan issue references with milestone scope.")
    if stale:
        action_candidates.append("Recheck stale open issues and update their authoritative state.")
    if not action_candidates:
        action_candidates.append("Choose one unclaimed READY issue from the verified backlog.")
    actions = "".join(f"<li>{esc(a)}</li>" for a in action_candidates[:3])
    snapshot = data.get("snapshot_at") or now.isoformat()
    project = data.get("project", "Project delivery")
    scope = milestone or "All milestones"
    plan_ref = link(plan.get("revision", "Unknown revision"), plan.get("url") or plan.get("source"))
    styles = """
    :root{font-family:Inter,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;color:#16283d;background:#f5f7fb}
    *{box-sizing:border-box}body{margin:0}header{background:#17283e;color:white;padding:40px max(24px,calc((100vw - 1150px)/2))}
    header h1{font-size:clamp(26px,4vw,38px);margin:8px 0}header p{color:#ccdae8}main{max-width:1150px;margin:auto;padding:26px 24px 60px}
    .eyebrow{text-transform:uppercase;letter-spacing:2px;font-size:11px;font-weight:800;color:#90c0df}
    .pills{display:flex;gap:10px;flex-wrap:wrap;margin-top:15px}.pill{border:1px solid #73869d;border-radius:40px;padding:7px 12px;font-size:12px}
    .metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px;margin:22px 0}.metric{background:white;border:1px solid #e1e7ef;border-radius:14px;padding:22px;display:flex;flex-direction:column;gap:7px}
    .metric strong{font-size:30px}.metric span{font-weight:750}.metric small{color:#5a6b80}
    .panel{background:white;border:1px solid #e1e7ef;border-radius:14px;padding:23px;margin:18px 0;box-shadow:0 4px 20px #18253e08}
    h2{font-size:19px;margin:0 0 16px}p,li{line-height:1.65}.subtle{color:#63758b;font-size:13px}
    .bar{background:#e7edf4;height:13px;border-radius:30px;overflow:hidden}.fill{background:#247b91;height:100%}
    table{width:100%;border-collapse:collapse;font-size:13px}th{text-align:left;color:#5a6b80;background:#f4f7fa}td,th{padding:12px;border-bottom:1px solid #e8edf3;vertical-align:top}
    a{color:#14758f;font-weight:600}ul{padding-left:19px}.scroll{overflow-x:auto}
    @media(max-width:760px){.metrics{grid-template-columns:repeat(2,1fr)}.panel{padding:16px}table{min-width:720px}}
    @media print{header{background:#17283e!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}.panel,.metric{break-inside:avoid}}
    """
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(project)} — Milestone status</title><style>{styles}</style></head>
<body><header><div class="eyebrow">AI-SDLC / DELIVERY INTELLIGENCE</div><h1>{esc(project)}</h1>
<p>{esc(scope)} · Snapshot {esc(snapshot)}</p><div class="pills"><span class="pill">Reconciliation: {integrity}</span><span class="pill">Health: {risk}</span><span class="pill">Plan: {plan_ref}</span></div></header>
<main><div class="metrics">{cards}</div>
<section class="panel"><h2>Milestone execution</h2><p class="subtle">Plan matched to current issue numbers. Closed issues without verification are not counted as DONE.</p>
<div class="bar" role="progressbar" aria-label="Plan coverage" aria-valuenow="{coverage}" aria-valuemin="0" aria-valuemax="100"><div class="fill" style="width:{coverage}%"></div></div>
<p class="subtle">Status distribution: {esc(", ".join(f"{k}: {v}" for k,v in sorted(counts.items())) or "No issues")} · Stale open issues (21+ days): {len(stale)}</p></section>
<section class="panel"><h2>Plan vs GitHub</h2><div class="scroll"><table><thead><tr><th>Issue</th><th>Outcome</th><th>State</th><th>Plan</th><th>Dependencies</th><th>Last update</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></section>
<section class="panel"><h2>Reconciliation gaps</h2><ul>{gap_html}</ul></section>
<section class="panel"><h2>Recommended next actions</h2><ol>{actions}</ol></section>
<p class="subtle">Derived only from the supplied issue/plan snapshot. Missing plans, completion evidence and deadlines are not inferred.</p></main></body></html>"""

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path, help="Normalized snapshot JSON")
    parser.add_argument("--output", required=True, type=Path, help="Output HTML file")
    parser.add_argument("--milestone", help="Milestone title filter")
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(data, args.milestone), encoding="utf-8")
    print(str(args.output))

if __name__ == "__main__":
    main()
