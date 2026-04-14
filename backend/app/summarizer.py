from __future__ import annotations

import json
from openai import OpenAI

from .schemas import AnalysisResult, ClusterSummary, GroupSummaryRead, StatementStat


def _other_avg(cluster_idx: int, stmt_id: int, all_clusters: list[ClusterSummary]) -> float:
    """Mean vote for a statement across all clusters except the given one."""
    others = [c.mean_votes.get(stmt_id, 0) for c in all_clusters if c.k != cluster_idx]
    return sum(others) / len(others) if others else 0.0


def build_prompt(
    cluster: ClusterSummary,
    all_clusters: list[ClusterSummary],
    statements: list[StatementStat],
    k: int,
    used_labels: list[str],
) -> str:
    idx = cluster.k
    mean = cluster.mean_votes

    # Per-cluster delta: statements where THIS group differs most from the others
    deltas = []
    for s in statements:
        this_val = mean.get(s.id, 0)
        other_val = _other_avg(idx, s.id, all_clusters)
        delta = this_val - other_val
        deltas.append((s, this_val, other_val, delta))

    top_delta = sorted(deltas, key=lambda x: abs(x[3]), reverse=True)[:8]

    strong_agree = sorted(
        [(s, v) for s, v, _, _ in deltas if v > 0.4],
        key=lambda x: x[1],
        reverse=True,
    )[:5]
    strong_disagree = sorted(
        [(s, v) for s, v, _, _ in deltas if v < -0.4],
        key=lambda x: x[1],
    )[:5]

    lines = [
        "You are analyzing results from a structured political opinion survey.",
        "",
        "Participants voted Agree (+1), Disagree (-1), or Pass (0) on statements.",
        f"They were grouped by voting similarity using PCA + k-means into {k} groups.",
        f"You are describing GROUP {idx + 1} of {k} ({cluster.size} participant{'s' if cluster.size != 1 else ''}).",
        "",
        "Statements where THIS group differs most from the other groups",
        "(delta = this group's avg minus the average of all other groups):",
    ]
    for s, this_val, other_val, delta in top_delta:
        sign = "+" if delta >= 0 else ""
        lines.append(
            f'  - "{s.text}"'
            f" → this group: {this_val:+.2f}, others avg: {other_val:+.2f}, delta: {sign}{delta:.2f}"
        )

    if strong_agree:
        lines += ["", "This group's strongest agreements (avg > 0.4):"]
        for s, v in strong_agree:
            lines.append(f'  - "{s.text}" → {v:+.2f}')

    if strong_disagree:
        lines += ["", "This group's strongest disagreements (avg < -0.4):"]
        for s, v in strong_disagree:
            lines.append(f'  - "{s.text}" → {v:+.2f}')

    lines += ["", "Respond with a JSON object for this group:"]

    if used_labels:
        forbidden_words = sorted({w.lower() for label in used_labels for w in label.split()})
        lines += [
            "",
            f"ALREADY USED LABELS (from other groups): {', '.join(repr(l) for l in used_labels)}",
            f"FORBIDDEN WORDS — your label MUST NOT contain any of these: {', '.join(forbidden_words)}",
            "Pick a label that uses entirely different words to describe this group's unique character.",
        ]

    lines += [
        "",
        "{",
        '  "label": "2-4 word name unique to this group — must not share any word with the forbidden list above",',
        '  "description": "2-3 sentences on what makes this group DISTINCT from the other groups",',
        '  "core_beliefs": ["belief 1", "belief 2", "belief 3"],',
        '  "key_disagreement": "One sentence on what most sets this group apart from the others"',
        "}",
    ]

    return "\n".join(lines)


def call_openai(api_key: str, prompt: str) -> dict:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.7,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a political analyst. Always respond with a valid JSON object only.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    raw = response.choices[0].message.content
    return json.loads(raw)


def generate_summaries(
    api_key: str,
    result: AnalysisResult,
) -> list[GroupSummaryRead]:
    summaries: list[GroupSummaryRead] = []
    used_labels: list[str] = []

    for cluster in result.clusters:
        prompt = build_prompt(cluster, result.clusters, result.statements, result.k, used_labels)
        data = call_openai(api_key, prompt)

        core_beliefs = data.get("core_beliefs", [])
        if isinstance(core_beliefs, str):
            core_beliefs = [core_beliefs]
        core_beliefs = [str(b) for b in core_beliefs[:5]]

        label = str(data.get("label", f"Group {cluster.k + 1}"))
        used_labels.append(label)

        summaries.append(
            GroupSummaryRead(
                cluster_idx=cluster.k,
                label=label,
                description=str(data.get("description", "")),
                core_beliefs=core_beliefs,
                key_disagreement=str(data.get("key_disagreement", "")),
            )
        )

    return summaries
