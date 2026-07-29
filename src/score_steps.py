#!/usr/bin/env python3
"""Score agent step-extractions against ground-truth step-extractions.

For each ground-truth step (from ctf-step-extractions/), check whether an
agent's writeup/transcript (from any `*-step-extractions/` directory) shows
anchor evidence of having reached it. Matching is retrieval-style: a
ground-truth step's anchors are searched across the agent's *entire* pooled
step text, not just the agent step with the matching id/stage -- agents may
take a different number of steps than ground truth, cover one milestone
across several of their own steps, or reach steps out of order.

A ground-truth step counts as "reached" iff at least --min-anchor-hits of its
distinct anchors are found in the agent's pooled text (default: 1, i.e. any
single anchor hit counts). This is a deliberately loose first pass -- some
anchors are too generic in isolation to be reliable on their own (e.g. a bare
positional-argument index like "7"), and raising --min-anchor-hits is the
intended way to tighten matching once real output has been reviewed, rather
than hardcoding a generic-token blocklist.

Which agent step fields get searched is also a tunable parameter
(--anchor-fields, default "evidence_quote,outcome,anchors"). milestone is
excluded by default because the schema requires it stay a literal-free
paraphrase ("do not include literal commands, payloads, credentials,
offsets, or flags") -- it structurally cannot carry anchor evidence, and is
used instead for the separate milestone-to-milestone embedding signal below.
The agent's own `anchors` field ("at most 5 literal technical tokens copied
exactly from the Markdown") is included since it's the most direct analog to
a GT anchor. The agent's final_outcome.flag_value is always searched too,
regardless of --anchor-fields, as its own pseudo-step ("final_outcome") --
a model can state the correct flag there while only describing it abstractly
in its actual steps.

A second, independent signal is milestone-embedding similarity: for each
ground-truth step, the model's own step milestones are ranked by cosine
similarity against it (Qwen3-Embedding-0.6B, local). This answers a different
question than anchors -- "did the model seem aware it needed to do this" --
and is purely exploratory context. It is NEVER used to decide "reached": a
model can describe the right concept while being on a completely wrong path,
which looks semantically close but has zero anchor evidence of actually
having done it. Anchors alone decide reached-ness; semantic similarity is
shown alongside for a human to read. Use --no-semantic to skip loading the
embedding model (e.g. for a fast anchor-only pass).

Multiple independent attempts ("runs") of the same solver on the same
challenge are supported via `Dataset/json/<challenge>/agent/<solver>/run-NN.json`
(run number parsed from the filename -- it is not, and does not need to be,
recorded inside the JSON body itself). A file with no parseable run number
is treated as a single run (run 1). All runs of one solver are scored
individually (identical code path regardless of whether there are 1 or many
runs) and then folded into one `models[]` entry with both the full per-run
detail (`runs`) and a cross-run summary (`aggregate`) -- see
`aggregate_runs()` for exactly what gets averaged/kept distinct and why.

`challenge` throughout this module means the `Dataset/json/<challenge>/`
folder name (e.g. "C01_crypto_ROT13") -- the canonical, category-coded task
id used in Dataset/README.md and INDEX.md. This is a different string from
the JSON's own internal `"challenge"` field (e.g. "crypto_picoctf5"), which
predates the Dataset/ reorg and is kept only as `challenge_slug` metadata in
the score output, never used for lookups.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from anchor_match import DEFAULT_ANCHOR_FIELDS, count_anchor_hits, normalize, step_text
from qwen_embed import DEFAULT_MODEL, embed, load_model
from sentence_transformers import util

ROOT = Path(__file__).parent.parent
DATASET_DIR = ROOT / "Dataset" / "json"
OUTPUT_DIR = ROOT / "output" / "step_scores"
TOP_K_SEMANTIC = 3
RUN_RE = re.compile(r"run-(\d+)")


def load_ground_truth(challenge: str) -> dict:
    path = DATASET_DIR / challenge / "reference.json"
    if not path.exists():
        raise FileNotFoundError(f"No reference.json for challenge {challenge!r} under {DATASET_DIR}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_agent_files(challenge: str) -> list[dict]:
    """One entry per (solver, run) combination found under
    Dataset/json/<challenge>/agent/<solver>/run-NN.json. Solver name comes
    from the directory name, not the filename. Empty leftover solver
    directories (a packaging artifact seen in some drops) are silently
    skipped since the run-*.json glob simply returns nothing for them."""
    entries = []
    agent_root = DATASET_DIR / challenge / "agent"
    if not agent_root.is_dir():
        return entries
    for solver_dir in sorted(p for p in agent_root.iterdir() if p.is_dir()):
        for path in sorted(solver_dir.glob("run-*.json")):
            m = RUN_RE.search(path.stem)
            run = int(m.group(1)) if m else 1
            entries.append({"solver": solver_dir.name, "run": run, "data": json.loads(path.read_text(encoding="utf-8"))})
    return entries


def group_by_solver(entries: list[dict]) -> dict[str, list[dict]]:
    """Group (solver, run) entries by solver, ordered by parsed run number
    (NOT filename string order -- "run-10" sorts before "run-2" lexically,
    so this must sort on the parsed int)."""
    by_solver: dict[str, list[dict]] = {}
    for e in sorted(entries, key=lambda e: (e["solver"], e["run"])):
        by_solver.setdefault(e["solver"], []).append(e)
    for solver, runs in by_solver.items():
        run_nums = [r["run"] for r in runs]
        if len(run_nums) != len(set(run_nums)):
            print(f"WARNING: duplicate run numbers for solver={solver!r} in one challenge: {run_nums}", file=sys.stderr)
    return by_solver


def available_challenges() -> list[str]:
    return sorted(p.name for p in DATASET_DIR.iterdir() if p.is_dir() and (p / "reference.json").exists())


def top_semantic_matches(gt_emb, agent_steps: list[dict], agent_emb, gt_index: int) -> list[dict]:
    """Rank the agent's own steps by milestone-embedding similarity to one
    ground-truth step. Descriptive only -- see module docstring. Per-run
    only: this never gets averaged across runs (see aggregate_runs)."""
    if agent_emb is None:
        return []
    sims = util.cos_sim(gt_emb[gt_index], agent_emb)[0].float().cpu().numpy()
    ranked = sorted(range(len(agent_steps)), key=lambda j: -sims[j])[:TOP_K_SEMANTIC]
    return [
        {
            "agent_step_id": agent_steps[j]["id"],
            "agent_milestone": agent_steps[j]["milestone"],
            "score": float(sims[j]),
        }
        for j in ranked
    ]


def score_one_run(agent: dict, gt: dict, gt_emb, embed_model, anchor_fields: tuple[str, ...], min_anchor_hits: int) -> dict:
    """Score a single run's step-extraction against GT. Identical logic
    regardless of whether this run is 1-of-1 or 1-of-5 -- run count is only
    relevant one level up, in aggregate_runs()."""
    agent_steps_by_id = {s["id"]: s for s in agent["steps"]}
    agent_step_texts = [(s["id"], step_text(s, anchor_fields)) for s in agent["steps"]]
    # The agent's final flag value is often stated only in final_outcome, not
    # reproduced literally in any individual step's evidence_quote/outcome/
    # milestone (a model can describe "the flag was recovered from the
    # README" without repeating the flag string in that step's text) --
    # search it as its own pseudo-step so a correct final flag still counts
    # as anchor evidence for the flag-recovery GT step.
    flag_value = agent.get("final_outcome", {}).get("flag_value")
    if flag_value:
        agent_step_texts.append(("final_outcome", normalize(flag_value)))
    agent_emb = embed(embed_model, [s["milestone"] for s in agent["steps"]]) if embed_model and agent["steps"] else None

    step_results = []
    for i, gt_step in enumerate(gt["steps"]):
        # Check each of the agent's own steps individually (not one pooled
        # blob) so we know *which* agent step(s) carried the evidence -- one
        # ground-truth step can be corroborated by several agent steps
        # (one-to-many), e.g. the agent splits one milestone across multiple
        # turns or repeats the same evidence later on.
        anchor_matches = []
        all_hits = set()
        for step_id, text in agent_step_texts:
            hits = count_anchor_hits(gt_step["anchors"], text)
            if not hits:
                continue
            if step_id == "final_outcome":
                quote = f"final_outcome.flag_value: {flag_value}"
            else:
                quote = agent_steps_by_id[step_id].get("evidence_quote")
            anchor_matches.append({"agent_step_id": step_id, "matched_anchors": hits, "evidence_quote": quote})
            all_hits.update(hits)
        # Best-evidenced match for this run (most anchors hit) -- used for
        # this run's own single "headline" evidence_quote; all matches are
        # still kept in anchor_matches for the expanded per-run detail view.
        best_match = max(anchor_matches, key=lambda m: len(m["matched_anchors"]), default=None)
        step_results.append(
            {
                "id": gt_step["id"],
                "reached": len(all_hits) >= min_anchor_hits,
                "matched_anchors": sorted(all_hits),
                "total_anchors": len(gt_step["anchors"]),
                "anchor_matches": anchor_matches,
                "evidence_quote": best_match["evidence_quote"] if best_match else None,
                "evidence_from": best_match["agent_step_id"] if best_match else None,
                "top_semantic": top_semantic_matches(gt_emb, agent["steps"], agent_emb, i) if gt_emb is not None else [],
            }
        )
    reached_stages = [gt["steps"][i]["stage"] for i, r in enumerate(step_results) if r["reached"]]
    gaps = [r["id"] for i, r in enumerate(step_results) if not r["reached"] and reached_stages and gt["steps"][i]["stage"] < max(reached_stages)]
    return {
        "n_steps": len(agent["steps"]),
        "flag_status": agent["final_outcome"]["flag_status"],
        "steps": step_results,
        "highest_reached_stage": max(reached_stages) if reached_stages else None,
        "gaps_below_highest": gaps,
    }


def aggregate_runs(runs: list[dict], gt_steps: list[dict]) -> dict:
    """Fold N per-run score_one_run() results into one cross-run summary.

    Design choices (deliberate, not arbitrary defaults):
    - Per-GT-step signal is a reached COUNT/fraction ("3/5"), not a boolean
      -- this is the actual new information multi-run data adds.
    - highest_reached_stage aggregates as the BEST (max) across runs, i.e.
      "how far can this model get at its best" -- the more decision-relevant
      capability question -- paired with gaps_below_highest_union computed
      relative to that same ceiling. The raw per-run values are preserved
      (highest_reached_stage_values) so a model that hits stage 5 once and
      stage 1 four times is still visibly different from one that hits
      stage 5 consistently -- the ceiling alone would hide that.
    - flag_status aggregates as a 3-way count (retrieved/not_retrieved/
      unknown), not collapsed to a single boolean -- "unknown" is kept
      distinct because it's ambiguous evidence, not a confirmed miss, and
      merging it into "not retrieved" would misrepresent it.
    - Semantic top-k is deliberately NOT aggregated at all -- it stays
      per-run only, visible in the expanded detail. Averaging embedding
      similarity across runs that may have taken completely different paths
      has no clean meaning, and semantic similarity is already
      "exploratory-only, never a reached-decider" per the module docstring;
      that same caution extends to not granting it aggregate authority.
    """
    n = len(runs)
    step_agg = []
    for i, gt_step in enumerate(gt_steps):
        reached_runs = [(r["run"], r["steps"][i]) for r in runs if r["steps"][i]["reached"]]
        best_run, best_step = max(reached_runs, key=lambda rs: len(rs[1]["matched_anchors"]), default=(None, None))
        step_agg.append(
            {
                "id": gt_step["id"],
                "reached_count": len(reached_runs),
                "n_runs": n,
                "representative_run": best_run,
                "representative_evidence_quote": best_step["evidence_quote"] if best_step else None,
            }
        )

    flag_counts = Counter(r["flag_status"] for r in runs)
    stage_values = [r["highest_reached_stage"] for r in runs]
    best_ceiling = max((v for v in stage_values if v is not None), default=None)
    gaps_union = [
        gt_steps[i]["id"]
        for i, s in enumerate(step_agg)
        if s["reached_count"] == 0 and best_ceiling is not None and gt_steps[i]["stage"] < best_ceiling
    ]

    return {
        "n_runs": n,
        "flag_status_counts": dict(flag_counts),
        "n_retrieved": flag_counts.get("retrieved", 0),
        "steps": step_agg,
        "highest_reached_stage_best": best_ceiling,
        "highest_reached_stage_values": stage_values,
        "gaps_below_highest_union": gaps_union,
    }


def score_challenge(challenge: str, min_anchor_hits: int, embed_model=None, anchor_fields: tuple[str, ...] = DEFAULT_ANCHOR_FIELDS) -> dict:
    gt = load_ground_truth(challenge)
    entries = load_agent_files(challenge)
    by_solver = group_by_solver(entries)

    gt_emb = embed(embed_model, [s["milestone"] for s in gt["steps"]]) if embed_model else None

    models = []
    for solver in sorted(by_solver):
        runs = []
        for entry in by_solver[solver]:
            run_result = score_one_run(entry["data"], gt, gt_emb, embed_model, anchor_fields, min_anchor_hits)
            run_result["run"] = entry["run"]
            runs.append(run_result)
        models.append(
            {
                "solver": solver,
                "n_runs": len(runs),
                "runs": runs,
                "aggregate": aggregate_runs(runs, gt["steps"]),
            }
        )

    return {
        "challenge": challenge,
        "challenge_slug": gt.get("challenge"),
        "min_anchor_hits": min_anchor_hits,
        "anchor_fields": list(anchor_fields),
        "n_gt_steps": len(gt["steps"]),
        "gt_steps": gt["steps"],
        "models": models,
    }


def print_grid(result: dict):
    gt_steps = result["gt_steps"]
    print(f"\n=== {result['challenge']} [{result['challenge_slug']}] (min_anchor_hits={result['min_anchor_hits']}, anchor_fields={result['anchor_fields']}) ===")
    step_col_width = 38
    header = "step".ljust(step_col_width) + "".join(f"{m['solver']}({m['n_runs']})"[:20].ljust(22) for m in result["models"])
    print(header)
    for i, s in enumerate(gt_steps):
        label = f"{s['id']} [{s['interaction_mode']}/{s['result_type']}]"
        row = label.ljust(step_col_width)
        for model in result["models"]:
            agg_step = model["aggregate"]["steps"][i]
            row += f"{agg_step['reached_count']}/{agg_step['n_runs']}".ljust(22)
        print(row)
    for model in result["models"]:
        agg = model["aggregate"]
        print(
            f"  {model['solver']} ({model['n_runs']} runs): best highest reached stage = "
            f"{agg['highest_reached_stage_best']}/{result['n_gt_steps']}, "
            f"flag {agg['n_retrieved']}/{model['n_runs']} retrieved, gaps below best ceiling = {agg['gaps_below_highest_union']}"
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--challenge", help="Score a single challenge by its Dataset/json/ folder name (e.g. C01_crypto_ROT13); default: all challenges")
    parser.add_argument("--min-anchor-hits", type=int, default=1, help="Distinct anchor hits required for a step to count as reached (default: 1)")
    parser.add_argument("--no-semantic", action="store_true", help="Skip the milestone-embedding similarity signal (anchor-only, faster)")
    parser.add_argument("--embed-model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--anchor-fields",
        default=",".join(DEFAULT_ANCHOR_FIELDS),
        help=f"Comma-separated agent step fields to search for GT anchors (default: {','.join(DEFAULT_ANCHOR_FIELDS)}). "
        "milestone is excluded by default since the schema requires it stay literal-free (it's used for the separate semantic signal instead).",
    )
    args = parser.parse_args()
    anchor_fields = tuple(f.strip() for f in args.anchor_fields.split(",") if f.strip())

    challenges = [args.challenge] if args.challenge else available_challenges()
    if not challenges:
        print("No agent data found.")
        return

    embed_model = None
    if not args.no_semantic:
        print(f"Loading {args.embed_model} ...", file=sys.stderr)
        embed_model = load_model(args.embed_model)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for challenge in challenges:
        result = score_challenge(challenge, args.min_anchor_hits, embed_model, anchor_fields)
        print_grid(result)
        out_path = OUTPUT_DIR / f"{challenge}.json"
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  -> wrote {out_path}")


if __name__ == "__main__":
    main()
