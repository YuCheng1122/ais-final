# Scoring methodology

Ground truth and agent solves share one schema (`ctf-step`, see
`Dataset/PROMPT.md` for the exact extraction spec): a challenge is split into
chronological `steps[]`, each with a literal-free `milestone`, a
`result_type`/`interaction_mode`/`status`, up to 5 verbatim `anchors[]`
tokens, and one `evidence_quote`.

Two independent signals, never conflated:

- **Anchor matching decides "reached"** (`anchor_match.py` +
  `score_steps.py:score_one_run`). A ground-truth step's anchors are searched
  across the agent's own step text (`evidence_quote`/`outcome`/`anchors` by
  default, plus `final_outcome.flag_value` as a pseudo-step) — literal token
  hits are the only evidence that counts. Loose by default
  (`--min-anchor-hits 1`); tighten via that flag once real output has been
  reviewed, rather than hardcoding a generic-token blocklist.
- **Milestone-embedding similarity is exploratory only**
  (`qwen_embed.py` + `top_semantic_matches`). Ranks the agent's own step
  milestones by cosine similarity to a ground-truth step. Answers "did the
  model seem aware it needed to do this," not "did it actually do it" — a
  model can describe the right concept while being on a completely wrong
  path. Always shown alongside the anchor verdict, never used to decide it.

`final_outcome.flag_status` (not any per-step `status`) is the only
challenge-level "did this run solve it" signal. A step's `result_type ==
"flag"` means that step produced flag-shaped output — not the same claim as
the run actually retrieving the flag.

Multiple runs per solver are supported (`Dataset/json/<challenge>/agent/
<solver>/run-XX.json`) and folded into a cross-run aggregate
(`aggregate_runs`): per-step reached counts as a fraction, highest-reached
stage as the best-case ceiling across runs (paired with the raw per-run
values so consistency is still visible), flag status as a 3-way
retrieved/not_retrieved/unknown count. Semantic top-k is never aggregated
across runs — it stays per-run, visible only in per-run detail.
