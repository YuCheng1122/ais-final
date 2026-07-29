"""Anchor-literal matching primitives for scoring agent step-extractions
against ground-truth step-extractions (the ``ctf-step`` schema).

Methodology (see METHODOLOGY.md, carried over from the old checkpoint
scoring approach): anchor literal hits are the only reliable "reached"
signal. Semantic/embedding similarity is exploratory only and must never
decide reached-ness on its own -- a model can talk *about* the right
concepts while being on a completely wrong path.

The ``ctf-step`` schema's anchors are already pre-extracted literal tokens
(unlike the old prose-style checkpoint anchors), so no regex literal
extraction step is needed here -- just normalize and substring-match.
"""

import re

WS_RE = re.compile(r"\s+")

# Fields worth searching for literal anchor evidence, per the schema's own
# field definitions:
#   - evidence_quote: verbatim quote -- always literal.
#   - outcome: observable result, not explicitly literal but often specific.
#   - anchors: "at most 5 literal technical tokens copied exactly from the
#     Markdown" -- the agent's own most direct analog to a GT anchor.
#   - milestone: schema explicitly REQUIRES it exclude literal commands/
#     payloads/credentials/offsets/flags ("neutral semantic summary in your
#     own words") -- structurally cannot carry anchor evidence, so it is
#     NOT in the default. It's still used separately for the milestone-to-
#     milestone embedding similarity signal, which is exactly what it's for.
DEFAULT_ANCHOR_FIELDS = ("evidence_quote", "outcome", "anchors")


def normalize(text: str) -> str:
    return WS_RE.sub(" ", text.lower()).strip()


def step_text(step: dict, fields: tuple[str, ...] = DEFAULT_ANCHOR_FIELDS) -> str:
    """Normalized text for one agent step, built from the given fields only.
    ``anchors`` is a list field and gets joined; everything else is a plain
    string field."""
    parts = []
    for f in fields:
        value = step.get(f)
        if not value:
            continue
        parts.append(" ".join(value) if isinstance(value, list) else value)
    return normalize("\n".join(parts))


def pool_agent_text(steps: list[dict], fields: tuple[str, ...] = DEFAULT_ANCHOR_FIELDS) -> str:
    """Concatenate the chosen fields across all of an agent's steps into one
    search pool, so a ground-truth step's anchors can be checked against
    everything the agent produced regardless of which of its own steps the
    agent happened to bucket that evidence under."""
    return normalize("\n".join(step_text(step, fields) for step in steps))


def anchor_hit(anchor: str, normalized_pool: str) -> bool:
    norm_anchor = normalize(anchor)
    if not norm_anchor:
        return False
    return norm_anchor in normalized_pool


def count_anchor_hits(anchors: list[str], normalized_pool: str) -> list[str]:
    """Return the subset of anchors that hit the pool (order preserved)."""
    return [a for a in anchors if anchor_hit(a, normalized_pool)]
