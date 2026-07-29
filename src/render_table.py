#!/usr/bin/env python3
"""Render the JSON output of score_steps.py into a self-contained HTML report:

- An "Overview" page (default view): per model, which challenges were solved
  (at least one run retrieved the flag) broken down by challenge category,
  and two failure matrices -- category x result_type and category x
  interaction_mode -- showing where a model tends to fail (fail/total GT
  steps of that combination, counted per run so a 5-run model contributes 5x
  the denominator of a 1-run model), so patterns like "this model misses
  credential-type steps in crypto challenges" are visible directly.
  Clicking any challenge (solved or not) jumps straight into its per-step
  detail table.
- A sidebar menu of individual challenges (so this scales as more test data
  / challenges get added), each with a table: rows = ground-truth steps,
  columns = models (one column per solver, regardless of how many runs that
  solver has -- runs are folded into an aggregate view by default with a
  click-to-expand detail panel per cell, never a column-per-run, since that
  would shrink column width to the point of being unreadable).

Each per-step cell shows, always visible (no hover-only tooltips):
  - the aggregate "N/n_runs reached" badge (the decision signal, anchor-hit
    based) plus one representative evidence_quote
  - a persistent (click-to-open, not hover) expand panel with full per-run
    detail: which of the agent's OWN steps carried the matching anchors for
    that run (a ground truth step can be corroborated by more than one agent
    step -- one-to-many), plus that run's top semantic (milestone-embedding)
    matches, shown purely as context, never as a second reached-decider.

Three fields that look similar but mean different things get visually
distinct treatment throughout, since conflating them was a real past
mis-read of this report:
  - steps[].status ("achieved"/"failed"/...) is per-MILESTONE and isn't
    rendered as a standalone signal at all here -- only the anchor-based
    `reached` badge (derived independently, not copied from this field) is.
  - final_outcome.flag_status ("retrieved"/"not_retrieved"/"unknown") is the
    only "did this run solve the challenge" signal -- rendered as a distinct
    pill-shaped `.flagbadge`, purple family, separate from the green/gray
    anchor-reached badges.
  - a GT step's result_type == "flag" means that STEP produced flag-shaped
    output, which is not the same as the run's flag_status -- marked with a
    small amber flag glyph next to the tag, not styled like either badge.
"""

import argparse
import html
import json
import re
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "step_scores"
REPORT_PATH = Path(__file__).parent.parent / "output" / "step_scores_table.html"

# `challenge` is now the Dataset/json/ folder name, e.g. "C01_crypto_ROT13"
# -- category is the topic segment right after the C/R/D + number prefix.
# (The 3 D-series challenges that used to be bare slugs with no topic prefix
# -- delulu/permuted/just_another_pickle_jail -- now live under
# D02_pwn_.../D01_crypto_.../D03_misc_... folder names, so this single regex
# covers them too; no override table needed any more.)
def category_of(challenge: str) -> str:
    m = re.match(r"^[A-Z]\d+_([a-z]+)_", challenge)
    return m.group(1) if m else "uncategorized"


# C/R/D = Contaminated/Recent/Deep, the Dataset/README.md data-provenance
# grouping -- an orthogonal dimension to category_of()'s topic grouping
# (a Contaminated challenge and a Deep challenge can both be "crypto").
CRD_LABELS = {"C": "Contaminated", "R": "Recent", "D": "Deep"}
CRD_ORDER = ["Contaminated", "Recent", "Deep"]


def crd_of(challenge: str) -> str:
    m = re.match(r"^([CRD])\d+_", challenge)
    return CRD_LABELS.get(m.group(1), "uncategorized") if m else "uncategorized"


CSS = """
* { box-sizing: border-box; }
body { font-family: system-ui, -apple-system, sans-serif; margin: 0; color: #1a1a1a; background: #fff; }
h1 { font-size: 1.2rem; margin: 0; padding: 1rem 1.5rem; border-bottom: 2px solid #333; }
h2 { font-size: 1.15rem; margin-top: 0; }
h3 { font-size: 1rem; margin: 1.2rem 0 0.4rem; }
.layout { display: flex; align-items: flex-start; }
.sidebar { width: 240px; flex: none; height: calc(100vh - 3.2rem); overflow-y: auto; border-right: 1px solid #ddd; padding: 0.75rem; position: sticky; top: 0; }
.sidebar input { width: 100%; padding: 5px 7px; margin-bottom: 8px; border: 1px solid #ccc; border-radius: 3px; font-size: 0.82rem; }
.sidebar button { display: block; width: 100%; text-align: left; padding: 7px 8px; margin-bottom: 3px; border: 1px solid #ddd; background: #fafafa; cursor: pointer; border-radius: 3px; font-size: 0.8rem; white-space: normal; overflow-wrap: anywhere; word-break: break-word; }
.sidebar button .n-models { float: right; color: #888; font-size: 0.72rem; margin-left: 4px; }
.sidebar button:hover { background: #eee; }
.sidebar button.active { background: #333; color: #fff; border-color: #333; }
.sidebar button.active .n-models { color: #ccc; }
.sidebar .overview-btn { font-weight: 700; border-color: #333; margin-bottom: 10px; }
.content { flex: 1; min-width: 0; padding: 1rem 1.5rem; padding-bottom: 42vh; }
.challenge-section { display: none; }
.challenge-section.active { display: block; }
.meta { color: #555; font-size: 0.85rem; margin-bottom: 1rem; }
.table-scroll { overflow-x: auto; margin-bottom: 1rem; border: 1px solid #eee; }
table { border-collapse: collapse; table-layout: fixed; }
th, td { border: 1px solid #ccc; padding: 6px 8px; vertical-align: top; font-size: 0.82rem; overflow-wrap: anywhere; word-break: break-word; }
th { background: #eee; text-align: left; }
col.step-col { width: 260px; }
col.model-col { width: 120px; }
.step-id { font-weight: 600; }
.step-tags { color: #666; font-size: 0.75rem; }
.rt-flag { color: #b8860b; font-weight: 700; }
.milestone { margin-top: 2px; }
.n-runs { color: #888; font-weight: 400; font-size: 0.74rem; }
.model-icon { vertical-align: -2px; margin-right: 4px; }
.badge { display: inline-block; padding: 1px 6px; border-radius: 3px; font-weight: 600; font-size: 0.78rem; white-space: nowrap; }
.badge.reached { background: #d4edda; color: #155724; }
.badge.not-reached { background: #e2e3e5; color: #555; }
.badge.frac { background: #d6e4f0; color: #1c4a72; cursor: pointer; }
.badge.frac:hover { background: #c2d8ec; }
.flagbadge { display: inline-block; padding: 2px 9px; border-radius: 10px; font-weight: 600; font-size: 0.78rem; margin-left: 6px; white-space: nowrap; }
.flagbadge.all { background: #e6d9f5; color: #5b2a86; }
.flagbadge.some { background: #f0e6fa; color: #7d4ea8; }
.flagbadge.none { background: #f5d9d9; color: #8a2b2b; }
.flagbadge.unknown { background: #eee; color: #666; }
.run-row:first-child { border-top: none; padding-top: 0; margin-top: 0; }
.run-row { margin: 4px 0 0; padding: 4px 0 0; border-top: 1px dotted #ddd; }
.run-label { font-family: monospace; font-weight: 600; margin-right: 4px; }
.anchor-match { margin: 3px 0 0 0; font-size: 0.76rem; }
.anchor-match .step-ref { font-family: monospace; background: #f0f0f0; padding: 0 3px; border-radius: 2px; }
.anchor-match .lits { font-family: monospace; color: #333; }
.anchor-match .quote { color: #555; font-style: italic; }
.semantic-list { margin-top: 6px; padding-top: 4px; border-top: 1px dashed #ddd; }
.semantic-item { font-size: 0.74rem; color: #444; margin: 1px 0; }
.semantic-item .score { font-family: monospace; font-weight: 600; }
.semantic-item .score.high { color: #b8860b; }
.semantic-item .gt-side { color: #666; }
mark.anchor-hit { background: #d4edda; color: #155724; padding: 0 1px; border-radius: 2px; }
.summary { font-size: 0.85rem; margin: 4px 0; }

.cat-name { font-weight: 600; text-transform: capitalize; }
.ch-link { display: inline-block; padding: 2px 7px; margin: 2px 3px 2px 0; border-radius: 3px; font-size: 0.76rem; cursor: pointer; border: 1px solid transparent; font-family: monospace; }
.ch-link.solved { background: #d4edda; color: #155724; }
.ch-link.failed { background: #f8d7da; color: #721c24; }
.ch-link:hover { filter: brightness(0.95); }
table.matrix th, table.matrix td { text-align: center; font-size: 0.78rem; padding: 5px; }
table.matrix td.empty { color: #bbb; }
table.matrix .cell-frac { font-family: monospace; font-weight: 600; }

table.model-summary { margin-bottom: 1rem; table-layout: auto; }
table.model-summary th, table.model-summary td { font-size: 0.8rem; padding: 4px 8px; }
.stage-list { color: #888; font-size: 0.72rem; margin-left: 4px; }
tr.model-summary-zh td { color: #666; font-size: 0.76rem; padding: 2px 8px 8px; border-top: none; background: #fbfbfb; }

table.leaderboard { margin-bottom: 1rem; table-layout: auto; width: 100%; }
table.leaderboard th, table.leaderboard td { text-align: center; font-size: 0.82rem; }
table.leaderboard th:first-child, table.leaderboard td:first-child { text-align: left; }
table.leaderboard td.empty { color: #bbb; }
.model-name { cursor: pointer; color: #0645ad; font-weight: 600; }
.model-name:hover { text-decoration: underline; }
tr.lb-detail { display: none; }
tr.lb-detail.open { display: table-row; }
tr.lb-detail td { background: #fafafa; text-align: left; padding: 10px 14px; }
tr.lb-detail h4 { margin: 0.7rem 0 0.3rem; font-size: 0.88rem; }
tr.lb-detail h4:first-child { margin-top: 0; }
.cat-chip-row { margin-bottom: 4px; }

.run-detail-panel { position: fixed; left: 240px; right: 0; bottom: 0; max-height: 38vh; overflow-y: auto;
  background: #fff; border-top: 2px solid #333; box-shadow: 0 -2px 12px rgba(0,0,0,0.15); padding: 10px 16px; display: none; z-index: 50; }
.run-detail-panel.open { display: block; }
.run-detail-panel .panel-head { display: flex; justify-content: space-between; align-items: center; font-weight: 700; font-size: 0.85rem; margin-bottom: 6px; font-family: monospace; }
.run-detail-panel .panel-close { cursor: pointer; color: #888; font-weight: 400; font-family: system-ui, sans-serif; }
.run-detail-panel .panel-close:hover { color: #222; }
.run-detail-panel .panel-body { font-size: 0.8rem; }
.run-detail-panel .panel-hint { color: #888; font-size: 0.8rem; }
"""

JS = """
function showChallenge(id) {
  document.querySelectorAll('.challenge-section').forEach(function(el) {
    el.classList.toggle('active', el.id === id);
  });
  document.querySelectorAll('.sidebar button').forEach(function(btn) {
    btn.classList.toggle('active', btn.dataset.target === id);
  });
}
function filterSidebar(query) {
  query = query.toLowerCase();
  document.querySelectorAll('.sidebar button[data-name]').forEach(function(btn) {
    btn.style.display = btn.dataset.name.toLowerCase().includes(query) ? '' : 'none';
  });
}
function toggleModelDetail(id) {
  document.getElementById(id).classList.toggle('open');
}
function showRunDetail(tmplId, title) {
  var tmpl = document.getElementById(tmplId);
  document.getElementById('run-detail-title').textContent = title;
  document.getElementById('run-detail-body').innerHTML = tmpl.innerHTML;
  document.getElementById('run-detail-panel').classList.add('open');
}
function closeRunDetail() {
  document.getElementById('run-detail-panel').classList.remove('open');
}
"""

SEMANTIC_HIGH_THRESHOLD = 0.6

# Vendor icons (Simple Icons project, CC0) embedded inline so the report
# stays a single self-contained file with no network dependency. Matched by
# substring against the solver name -- new model families just need one more
# entry here, no other code change.
MODEL_ICONS = {
    "llama": '<svg class="model-icon" viewBox="0 0 24 24" width="14" height="14" fill="#0467DF" xmlns="http://www.w3.org/2000/svg"><title>Meta</title><path d="M6.915 4.03c-1.968 0-3.683 1.28-4.871 3.113C.704 9.208 0 11.883 0 14.449c0 .706.07 1.369.21 1.973a6.624 6.624 0 0 0 .265.86 5.297 5.297 0 0 0 .371.761c.696 1.159 1.818 1.927 3.593 1.927 1.497 0 2.633-.671 3.965-2.444.76-1.012 1.144-1.626 2.663-4.32l.756-1.339.186-.325c.061.1.121.196.183.3l2.152 3.595c.724 1.21 1.665 2.556 2.47 3.314 1.046.987 1.992 1.22 3.06 1.22 1.075 0 1.876-.355 2.455-.843a3.743 3.743 0 0 0 .81-.973c.542-.939.861-2.127.861-3.745 0-2.72-.681-5.357-2.084-7.45-1.282-1.912-2.957-2.93-4.716-2.93-1.047 0-2.088.467-3.053 1.308-.652.57-1.257 1.29-1.82 2.05-.69-.875-1.335-1.547-1.958-2.056-1.182-.966-2.315-1.303-3.454-1.303zm10.16 2.053c1.147 0 2.188.758 2.992 1.999 1.132 1.748 1.647 4.195 1.647 6.4 0 1.548-.368 2.9-1.839 2.9-.58 0-1.027-.23-1.664-1.004-.496-.601-1.343-1.878-2.832-4.358l-.617-1.028a44.908 44.908 0 0 0-1.255-1.98c.07-.109.141-.224.211-.327 1.12-1.667 2.118-2.602 3.358-2.602zm-10.201.553c1.265 0 2.058.791 2.675 1.446.307.327.737.871 1.234 1.579l-1.02 1.566c-.757 1.163-1.882 3.017-2.837 4.338-1.191 1.649-1.81 1.817-2.486 1.817-.524 0-1.038-.237-1.383-.794-.263-.426-.464-1.13-.464-2.046 0-2.221.63-4.535 1.66-6.088.454-.687.964-1.226 1.533-1.533a2.264 2.264 0 0 1 1.088-.285z"/></svg>',
    "gemma": '<svg class="model-icon" viewBox="0 0 24 24" width="14" height="14" fill="#4285F4" xmlns="http://www.w3.org/2000/svg"><title>Google</title><path d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z"/></svg>',
    "nemotron": '<svg class="model-icon" viewBox="0 0 24 24" width="14" height="14" fill="#76B900" xmlns="http://www.w3.org/2000/svg"><title>NVIDIA</title><path d="M8.948 8.798v-1.43a6.7 6.7 0 0 1 .424-.018c3.922-.124 6.493 3.374 6.493 3.374s-2.774 3.851-5.75 3.851c-.398 0-.787-.062-1.158-.185v-4.346c1.528.185 1.837.857 2.747 2.385l2.04-1.714s-1.492-1.952-4-1.952a6.016 6.016 0 0 0-.796.035m0-4.735v2.138l.424-.027c5.45-.185 9.01 4.47 9.01 4.47s-4.08 4.964-8.33 4.964c-.37 0-.733-.035-1.095-.097v1.325c.3.035.61.062.91.062 3.957 0 6.82-2.023 9.593-4.408.459.371 2.34 1.263 2.73 1.652-2.633 2.208-8.772 3.984-12.253 3.984-.335 0-.653-.018-.971-.053v1.864H24V4.063zm0 10.326v1.131c-3.657-.654-4.673-4.46-4.673-4.46s1.758-1.944 4.673-2.262v1.237H8.94c-1.528-.186-2.73 1.245-2.73 1.245s.68 2.412 2.739 3.11M2.456 10.9s2.164-3.197 6.5-3.533V6.201C4.153 6.59 0 10.653 0 10.653s2.35 6.802 8.948 7.42v-1.237c-4.84-.6-6.492-5.936-6.492-5.936z"/></svg>',
    "opus": '<svg class="model-icon" viewBox="0 0 24 24" width="14" height="14" fill="#D97757" xmlns="http://www.w3.org/2000/svg"><title>Anthropic</title><path d="M17.3041 3.541h-3.6718l6.696 16.918H24Zm-10.6082 0L0 20.459h3.7442l1.3693-3.5527h7.0052l1.3693 3.5528h3.7442L10.5363 3.5409Zm-.3712 10.2232 2.2914-5.9456 2.2914 5.9456Z"/></svg>',
}


def model_icon(solver: str) -> str:
    key = solver.lower()
    for needle, svg in MODEL_ICONS.items():
        if needle in key:
            return svg
    return ""


def escape(text) -> str:
    return html.escape(str(text)) if text is not None else ""


def fail_color(fail: int, total: int) -> str:
    """Green (0% fail) -> red (100% fail), as an inline background style."""
    if total == 0:
        return ""
    ratio = fail / total
    hue = round(120 * (1 - ratio))  # 120=green, 0=red
    return f"background: hsl({hue}, 65%, 88%);"


def result_type_tag(rt: str) -> str:
    """result_type == 'flag' means this STEP produced flag-shaped output --
    not the same thing as the run's final_outcome.flag_status. Marked with a
    small amber glyph so it never reads as "flag captured" on its own."""
    if rt == "flag":
        return f'{escape(rt)} <span class="rt-flag" title="this step produced flag-shaped output -- see flag_status for whether the run actually retrieved the flag">&#9873;</span>'
    return escape(rt)


def flag_class(agg: dict) -> str:
    n = sum(agg["flag_status_counts"].values())
    if n == 0 or agg["n_retrieved"] == 0:
        if agg["flag_status_counts"].get("unknown", 0) == n and n > 0:
            return "unknown"
        return "none"
    if agg["n_retrieved"] == n:
        return "all"
    return "some"


def render_flagbadge(agg: dict, n_runs: int, compact: bool = False) -> str:
    unknown = agg["flag_status_counts"].get("unknown", 0)
    extra = f", {unknown} unknown" if unknown else ""
    label = f"{agg['n_retrieved']}/{n_runs}" if compact else f"flag_status: {agg['n_retrieved']}/{n_runs} retrieved"
    return (
        f'<span class="flagbadge {flag_class(agg)}" '
        f'title="final_outcome.flag_status across runs -- the only signal for whether a run actually retrieved the flag">'
        f"{label}{extra}</span>"
    )


def render_model_summary_zh(model: dict, result: dict) -> str:
    """A rule-based (not LLM-generated) Traditional Chinese sentence
    summarizing one model's aggregate performance on one challenge, built
    entirely from fields aggregate_runs() already computed. Since it's a
    template over live aggregate data, it never goes stale -- no caching or
    regeneration step is needed when new run data is added, unlike an
    LLM-generated summary would require."""
    agg = model["aggregate"]
    n_runs = model["n_runs"]
    n_gt_steps = result["n_gt_steps"]
    stage_list = "、".join(str(v) if v is not None else "-" for v in agg["highest_reached_stage_values"])

    counts = agg["flag_status_counts"]
    flag_parts = []
    if counts.get("retrieved"):
        flag_parts.append(f"{counts['retrieved']} 次成功")
    if counts.get("unknown"):
        flag_parts.append(f"{counts['unknown']} 次未知")
    if counts.get("not_retrieved"):
        flag_parts.append(f"{counts['not_retrieved']} 次未取得")
    flag_summary = "、".join(flag_parts) if flag_parts else "無資料"

    gaps = "、".join(agg["gaps_below_highest_union"]) if agg["gaps_below_highest_union"] else "無"

    return (
        f"此模型執行 {n_runs} 次，最高抵達第 {agg['highest_reached_stage_best']}/{n_gt_steps} 關"
        f"（各次：{stage_list}），flag 取得 {flag_summary}。"
        f"相對最佳表現尚未跨越：{gaps}。"
    )


def js_str(text) -> str:
    """Escape for embedding as a single-quoted JS string literal inside an
    HTML attribute (the attribute value as a whole still gets html.escape()
    on top, which is what turns the quote we insert here into an HTML entity
    that decodes back to a literal quote before JS ever sees it)."""
    return str(text).replace("\\", "\\\\").replace("'", "\\'")


def highlight_anchors(text: str, anchors: list[str]) -> str:
    """Wrap the substring(s) of `text` that made an anchor hit in <mark>, so
    the evidence_quote visually shows *which word* matched instead of just
    listing the anchor tokens beside it. Matching mirrors anchor_match.py's
    normalize() (case-insensitive, whitespace-collapsed) but is applied to
    the original-cased text so the highlighted span reads naturally.

    A matched anchor won't always appear verbatim inside this particular
    quote -- anchor_match.py also searches the step's outcome/anchors fields,
    so a hit can come from elsewhere. Anchors not found here are silently
    skipped (no highlight), never force-matched."""
    if not text or not anchors:
        return escape(text)
    patterns = []
    for a in anchors:
        a = a.strip()
        if not a:
            continue
        pattern = r"\s+".join(re.escape(w) for w in a.split())
        if pattern:
            patterns.append(pattern)
    if not patterns:
        return escape(text)
    combined = re.compile("(" + "|".join(patterns) + ")", re.IGNORECASE)
    parts = combined.split(text)
    return "".join(
        f"<mark class=\"anchor-hit\">{escape(part)}</mark>" if i % 2 else escape(part)
        for i, part in enumerate(parts)
    )


def render_cell(agg_step: dict, runs: list[dict], i: int, tmpl_id: str, title: str, gt_milestone: str) -> str:
    """Renders just a small clickable fraction badge plus an inert <template>
    holding the full per-run detail. The detail is never inlined into the
    table itself (that was the old <details> design) -- it gets cloned into
    a single shared panel on click (see showRunDetail() in JS) specifically
    so opening detail for one cell can never inflate that table row's height,
    which was dragging the whole row (including the unrelated GT-step label
    column) tall along with it."""
    n = agg_step["n_runs"]
    badge = (
        f'<span class="badge frac" onclick="showRunDetail(\'{escape(js_str(tmpl_id))}\', \'{escape(js_str(title))}\')">'
        f"{agg_step['reached_count']}/{n}</span>"
    )

    detail_rows = []
    for run in runs:
        step = run["steps"][i]
        badge_class = "reached" if step["reached"] else "not-reached"
        badge_text = f"OK {len(step['matched_anchors'])}/{step['total_anchors']}" if step["reached"] else "not reached"
        row = [
            f'<div class="run-row"><span class="run-label">run-{run["run"]:02d}</span> '
            f'<span class="badge {badge_class}">{escape(badge_text)}</span>'
        ]
        for m in step["anchor_matches"]:
            lits = ", ".join(escape(a) for a in m["matched_anchors"])
            quote_text = highlight_anchors(m["evidence_quote"], m["matched_anchors"]) if m.get("evidence_quote") else ""
            quote = f' <span class="quote">&ldquo;{quote_text}&rdquo;</span>' if quote_text else ""
            row.append(
                f'<div class="anchor-match"><span class="step-ref">{escape(m["agent_step_id"])}</span> '
                f'<span class="lits">{lits}</span>{quote}</div>'
            )
        if step["top_semantic"]:
            sem_html = ['<div class="semantic-list">']
            for s in step["top_semantic"]:
                score_class = "score high" if s["score"] >= SEMANTIC_HIGH_THRESHOLD else "score"
                sem_html.append(
                    f'<div class="semantic-item"><span class="{score_class}">{s["score"]:.2f}</span> '
                    f'<span class="step-ref">{escape(s["agent_step_id"])}</span> '
                    f'<span class="gt-side">GT:&nbsp;&ldquo;{escape(gt_milestone)}&rdquo;</span> '
                    f"&harr; Agent:&nbsp;&ldquo;{escape(s['agent_milestone'])}&rdquo;</div>"
                )
            sem_html.append("</div>")
            row.append("".join(sem_html))
        row.append("</div>")
        detail_rows.append("".join(row))

    return f'{badge}<template id="{escape(tmpl_id)}">{"".join(detail_rows)}</template>'


def render_challenge(result: dict, section_id: str, active: bool) -> str:
    gt_steps = result["gt_steps"]
    cls = "challenge-section active" if active else "challenge-section"
    out = [f'<div class="{cls}" id="{escape(section_id)}">']
    out.append(
        f'<h2>{escape(result["challenge"])} '
        f'<span class="step-tags">({category_of(result["challenge"])} &middot; {crd_of(result["challenge"])})</span></h2>'
    )
    out.append(
        f'<div class="meta">challenge slug: {escape(result.get("challenge_slug"))} &middot; '
        f'min_anchor_hits = {result["min_anchor_hits"]} &middot; {result["n_gt_steps"]} ground-truth steps '
        f"&middot; click any &ldquo;N/n&rdquo; badge below to see that model's per-run detail (anchor matches, evidence quotes, semantic "
        f"context, score {SEMANTIC_HIGH_THRESHOLD}+ highlighted amber, never decisive) in the panel at the bottom of the screen "
        f"&middot; that badge and the purple flag_status badge above are independent signals -- a step can be reached without the flag being retrieved, and vice versa</div>"
    )

    out.append(
        '<table class="model-summary"><thead><tr><th>Model</th><th>Runs</th>'
        "<th>Best stage</th><th>Flag</th><th>Gaps below best</th></tr></thead><tbody>"
    )
    for model in result["models"]:
        agg = model["aggregate"]
        stage_list = ", ".join(str(v) if v is not None else "-" for v in agg["highest_reached_stage_values"])
        gaps = ", ".join(agg["gaps_below_highest_union"]) if agg["gaps_below_highest_union"] else "-"
        out.append(
            f'<tr><td>{model_icon(model["solver"])}{escape(model["solver"])}</td><td>{model["n_runs"]}</td>'
            f'<td>{agg["highest_reached_stage_best"]}/{result["n_gt_steps"]} <span class="stage-list">[{stage_list}]</span></td>'
            f'<td>{render_flagbadge(agg, model["n_runs"], compact=True)}</td>'
            f"<td>{escape(gaps)}</td></tr>"
        )
        out.append(
            f'<tr class="model-summary-zh"><td colspan="5">{escape(render_model_summary_zh(model, result))}</td></tr>'
        )
    out.append("</tbody></table>")

    out.append('<div class="table-scroll"><table><colgroup>')
    out.append('<col class="step-col">')
    for _ in result["models"]:
        out.append('<col class="model-col">')
    out.append("</colgroup><thead><tr><th>Ground-truth step</th>")
    for model in result["models"]:
        out.append(f'<th>{model_icon(model["solver"])}{escape(model["solver"])} <span class="n-runs">({model["n_runs"]} run{"s" if model["n_runs"] != 1 else ""})</span></th>')
    out.append("</tr></thead><tbody>")

    for i, s in enumerate(gt_steps):
        out.append("<tr>")
        out.append(
            f'<td><div class="step-id">{escape(s["id"])} (stage {s["stage"]})</div>'
            f'<div class="step-tags">{escape(s["interaction_mode"])} / {result_type_tag(s["result_type"])}</div>'
            f'<div class="milestone">{escape(s["milestone"])}</div></td>'
        )
        for mi, model in enumerate(result["models"]):
            tmpl_id = f"tmpl-{section_id}-{i}-{mi}"
            title = f"{model['solver']} — {s['id']} (stage {s['stage']})"
            out.append(f'<td>{render_cell(model["aggregate"]["steps"][i], model["runs"], i, tmpl_id, title, s["milestone"])}</td>')
        out.append("</tr>")
    out.append("</tbody></table></div></div>")
    return "".join(out)


def compute_overview(results: list[dict], section_id_of: dict[str, str]) -> dict:
    """Per-model: solved/total per category (solved = at least one run
    retrieved the flag -- ceiling semantics, consistent with
    highest_reached_stage_best), plus fail/total matrices by result_type and
    interaction_mode, each broken down by challenge category, counted in RUN
    units (a 5-run solver contributes 5x the denominator of a 1-run solver
    for the same GT step -- this is a strict generalization of the old
    one-file-per-model counting, byte-identical for any solver with exactly
    1 run)."""
    solvers = sorted({m["solver"] for r in results for m in r["models"]})
    result_types, interaction_modes = set(), set()
    per_model = {s: {"categories": {}, "crd": {}, "rt_matrix": {}, "im_matrix": {}, "n_solved": 0, "n_total": 0} for s in solvers}

    for result in results:
        challenge = result["challenge"]
        cat = category_of(challenge)
        crd = crd_of(challenge)
        section_id = section_id_of[challenge]
        gt_steps = result["gt_steps"]
        for model in result["models"]:
            solver = model["solver"]
            agg = model["aggregate"]
            bucket = per_model[solver]
            # "solved" = at least one run's final_outcome.flag_status is
            # "retrieved" -- optimistic/ceiling semantics, mirrors
            # highest_reached_stage_best. NOT the flag-type GT step's
            # anchor-based `reached` (that's a fragile proxy -- some
            # challenges don't even list the flag literal among that step's
            # anchors).
            solved = agg["n_retrieved"] > 0

            chip = {
                "challenge": challenge,
                "section_id": section_id,
                "solved": solved,
                "fraction": f"{agg['n_retrieved']}/{model['n_runs']}",
            }
            cat_bucket = bucket["categories"].setdefault(cat, {"solved": 0, "total": 0, "challenges": []})
            cat_bucket["total"] += 1
            cat_bucket["solved"] += int(solved)
            cat_bucket["challenges"].append(chip)

            crd_bucket = bucket["crd"].setdefault(crd, {"solved": 0, "total": 0, "challenges": []})
            crd_bucket["total"] += 1
            crd_bucket["solved"] += int(solved)
            crd_bucket["challenges"].append(chip)

            bucket["n_total"] += 1
            bucket["n_solved"] += int(solved)

            for i, gt_step in enumerate(gt_steps):
                result_types.add(gt_step["result_type"])
                interaction_modes.add(gt_step["interaction_mode"])
                step_agg = agg["steps"][i]
                fail = step_agg["n_runs"] - step_agg["reached_count"]
                rt_cell = bucket["rt_matrix"].setdefault(cat, {}).setdefault(gt_step["result_type"], {"fail": 0, "total": 0})
                rt_cell["total"] += step_agg["n_runs"]
                rt_cell["fail"] += fail
                im_cell = bucket["im_matrix"].setdefault(cat, {}).setdefault(gt_step["interaction_mode"], {"fail": 0, "total": 0})
                im_cell["total"] += step_agg["n_runs"]
                im_cell["fail"] += fail

    return {
        "solvers": solvers,
        "result_types": sorted(result_types),
        "interaction_modes": sorted(interaction_modes),
        "per_model": per_model,
    }


def render_matrix(bucket: dict, categories: list[str], columns: list[str]) -> str:
    out = ['<table class="matrix"><thead><tr><th>Category</th>']
    out.extend(f"<th>{escape(c)}</th>" for c in columns)
    out.append("</tr></thead><tbody>")
    for cat in categories:
        out.append(f'<tr><td class="cat-name">{escape(cat)}</td>')
        row = bucket.get(cat, {})
        for col in columns:
            cell = row.get(col)
            if not cell or cell["total"] == 0:
                out.append('<td class="empty">&ndash;</td>')
            else:
                style = fail_color(cell["fail"], cell["total"])
                out.append(f'<td style="{style}"><span class="cell-frac">{cell["fail"]}/{cell["total"]}</span> fail</td>')
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def render_overview(overview: dict, active: bool) -> str:
    cls = "challenge-section active" if active else "challenge-section"
    out = [f'<div class="{cls}" id="overview">']
    out.append("<h2>Overview</h2>")
    out.append(
        '<div class="meta">Solved = at least one run\'s final_outcome.flag_status is "retrieved" (best-case, same ceiling semantics as the '
        "per-challenge table's highest-reached-stage). Click a model name to expand its challenge list and fail-rate detail. "
        "Fail matrices are counted in run units: among all runs scored against a GT step of that (category, type) combination, "
        "how many did NOT anchor-reach it (a 5-run solver contributes 5x the denominator of a 1-run solver for the same step).</div>"
    )

    all_categories = sorted({cat for m in overview["per_model"].values() for cat in m["categories"]})
    all_crd = [c for c in CRD_ORDER if any(c in m["crd"] for m in overview["per_model"].values())]
    ranked = sorted(
        overview["solvers"],
        key=lambda s: (-overview["per_model"][s]["n_solved"] / max(overview["per_model"][s]["n_total"], 1), s),
    )

    out.append('<table class="leaderboard"><thead><tr><th>Model</th><th>Solved</th>')
    out.extend(f"<th>{escape(cat)}</th>" for cat in all_categories)
    out.extend(f'<th title="data source">{escape(crd)}</th>' for crd in all_crd)
    out.append("</tr></thead><tbody>")

    for solver in ranked:
        bucket = overview["per_model"][solver]
        detail_id = f"lbdetail-{solver}"
        out.append(
            '<tr class="lb-row"><td>'
            f'<span class="model-name" onclick="toggleModelDetail(\'{detail_id}\')">{model_icon(solver)}{escape(solver)} &#9656;</span>'
            f"</td><td>{bucket['n_solved']}/{bucket['n_total']}</td>"
        )
        for cat in all_categories:
            cb = bucket["categories"].get(cat)
            out.append(f"<td>{cb['solved']}/{cb['total']}</td>" if cb else '<td class="empty">&ndash;</td>')
        for crd in all_crd:
            cb = bucket["crd"].get(crd)
            out.append(f"<td>{cb['solved']}/{cb['total']}</td>" if cb else '<td class="empty">&ndash;</td>')
        out.append("</tr>")

        out.append(f'<tr class="lb-detail" id="{escape(detail_id)}"><td colspan="{2 + len(all_categories) + len(all_crd)}">')
        out.append("<h4>Challenges by category</h4>")
        for cat in sorted(bucket["categories"]):
            cb = bucket["categories"][cat]
            out.append(f'<div class="cat-chip-row"><span class="cat-name">{escape(cat)}</span> ')
            for ch in sorted(cb["challenges"], key=lambda c: c["challenge"]):
                link_cls = "ch-link solved" if ch["solved"] else "ch-link failed"
                out.append(f'<span class="{link_cls}" onclick="showChallenge(\'{ch["section_id"]}\')">{escape(ch["challenge"])} {escape(ch["fraction"])}</span>')
            out.append("</div>")

        out.append("<h4>Challenges by data source (Contaminated / Recent / Deep)</h4>")
        for crd in [c for c in CRD_ORDER if c in bucket["crd"]]:
            cb = bucket["crd"][crd]
            out.append(f'<div class="cat-chip-row"><span class="cat-name">{escape(crd)}</span> ')
            for ch in sorted(cb["challenges"], key=lambda c: c["challenge"]):
                link_cls = "ch-link solved" if ch["solved"] else "ch-link failed"
                out.append(f'<span class="{link_cls}" onclick="showChallenge(\'{ch["section_id"]}\')">{escape(ch["challenge"])} {escape(ch["fraction"])}</span>')
            out.append("</div>")

        out.append("<h4>Fail rate by category &times; result_type</h4>")
        out.append(render_matrix(bucket["rt_matrix"], sorted(bucket["categories"]), overview["result_types"]))

        out.append("<h4>Fail rate by category &times; interaction_mode</h4>")
        out.append(render_matrix(bucket["im_matrix"], sorted(bucket["categories"]), overview["interaction_modes"]))

        out.append("</td></tr>")

    out.append("</tbody></table>")
    out.append("</div>")
    return "".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenge", help="Render a single challenge; default: all files in output/step_scores/")
    args = parser.parse_args()

    if args.challenge:
        paths = [OUTPUT_DIR / f"{args.challenge}.json"]
    else:
        paths = sorted(OUTPUT_DIR.glob("*.json"))

    if not paths:
        print(f"No score files found in {OUTPUT_DIR} -- run score_steps.py first.")
        return

    results = [json.loads(p.read_text(encoding="utf-8")) for p in paths]

    section_id_of = {result["challenge"]: f"ch-{i}" for i, result in enumerate(results)}

    sidebar_items = [
        '<button class="overview-btn" data-target="overview" onclick="showChallenge(\'overview\')">Overview</button>'
    ]
    sections = [render_overview(compute_overview(results, section_id_of), active=(not args.challenge))]
    for i, result in enumerate(results):
        section_id = section_id_of[result["challenge"]]
        n_models = len(result["models"])
        sidebar_items.append(
            f'<button data-target="{section_id}" data-name="{escape(result["challenge"])}"'
            f' onclick="showChallenge(\'{section_id}\')">'
            f'{escape(result["challenge"])}<span class="n-models">{n_models}</span></button>'
        )
        sections.append(render_challenge(result, section_id, active=bool(args.challenge)))

    html_doc = (
        "<!doctype html><html><head><meta charset='utf-8'><title>Step scoring</title>"
        f"<style>{CSS}</style></head><body>"
        "<h1>CTF step-extraction scoring: ground truth vs agent runs</h1>"
        '<div class="layout">'
        '<div class="sidebar">'
        '<input type="text" placeholder="Filter challenges..." oninput="filterSidebar(this.value)">'
        f"{''.join(sidebar_items)}"
        "</div>"
        f'<div class="content">{"".join(sections)}</div>'
        "</div>"
        '<div class="run-detail-panel" id="run-detail-panel">'
        '<div class="panel-head"><span id="run-detail-title"></span>'
        '<span class="panel-close" onclick="closeRunDetail()">&times; close</span></div>'
        '<div class="panel-body" id="run-detail-body"></div>'
        "</div>"
        f"<script>{JS}</script></body></html>"
    )
    REPORT_PATH.write_text(html_doc, encoding="utf-8")
    print(f"Wrote {REPORT_PATH} ({len(results)} challenges)")


if __name__ == "__main__":
    main()
