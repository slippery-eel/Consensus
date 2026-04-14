from __future__ import annotations

import json
from openai import OpenAI

from .schemas import AnalysisResult, ClusterSummary, GroupSummaryRead, StatementStat


def _other_avg(cluster_idx: int, stmt_id: int, all_clusters: list[ClusterSummary]) -> float:
    """Mean vote for a statement across all clusters except the given one."""
    others = [c.mean_votes.get(stmt_id, 0) for c in all_clusters if c.k != cluster_idx]
    return sum(others) / len(others) if others else 0.0


def build_prompt(
    all_clusters: list[ClusterSummary],
    statements: list[StatementStat],
    k: int,
) -> str:
    lines = [
        "You are analyzing results from a structured political opinion survey.",
        "",
        "Participants voted Agree (+1), Disagree (-1), or Pass (0) on statements.",
        f"They were grouped by voting similarity using PCA + k-means into {k} groups.",
        "",
        f"Below are all {k} groups. For each group you will see:",
        "  - Statements where THIS group differs most from the other groups (delta = this group minus others' average)",
        "  - This group's strongest agreements and disagreements",
        "",
    ]

    for cluster in all_clusters:
        idx = cluster.k
        mean = cluster.mean_votes

        # Per-cluster delta: how differently does THIS cluster rate each statement vs others?
        deltas = []
        for s in statements:
            this_val = mean.get(s.id, 0)
            other_val = _other_avg(idx, s.id, all_clusters)
            delta = this_val - other_val
            deltas.append((s, this_val, other_val, delta))

        # Top 8 by absolute delta — these are the statements that make this group unique
        top_delta = sorted(deltas, key=lambda x: abs(x[3]), reverse=True)[:8]

        # Strong agreements and disagreements specific to this cluster
        strong_agree = sorted(
            [(s, v) for s, v, _, _ in deltas if v > 0.4],
            key=lambda x: x[1],
            reverse=True,
        )[:5]
        strong_disagree = sorted(
            [(s, v) for s, v, _, _ in deltas if v < -0.4],
            key=lambda x: x[1],
        )[:5]

        lines += [
            f"━━━ GROUP {idx + 1} of {k} ({cluster.size} participant{'s' if cluster.size != 1 else ''}) ━━━",
            "",
            "Statements where this group diverges most from the others:",
        ]
        for s, this_val, other_val, delta in top_delta:
            sign = "+" if delta >= 0 else ""
            lines.append(
                f'  - "{s.text}"'
                f" → this group: {this_val:+.2f}, others avg: {other_val:+.2f}, delta: {sign}{delta:.2f}"
            )

        if strong_agree:
            lines += ["", "Strongest agreements (avg > 0.4):"]
            for s, v in strong_agree:
                lines.append(f'  - "{s.text}" → {v:+.2f}')

        if strong_disagree:
            lines += ["", "Strongest disagreements (avg < -0.4):"]
            for s, v in strong_disagree:
                lines.append(f'  - "{s.text}" → {v:+.2f}')

        lines.append("")

    # Cross-group consensus (for context — these don't distinguish groups)
    consensus = [s for s in statements if s.is_consensus]
    if consensus:
        lines += [
            "Statements the whole survey broadly agreed on (NOT group-distinguishing):",
        ]
        for s in consensus:
            lines.append(f'  - "{s.text}"')
        lines.append("")

    lines += [
        f"Return a JSON array of exactly {k} objects, one per group, in order from Group 1 to Group {k}:",
        "[",
        "  {",
        '    "group": 1,',
        '    "label": "2-4 word name that captures what is UNIQUE about this group",',
        '    "description": "2-3 sentences focusing on what makes this group DISTINCT from the other groups — not just what they believe, but how they differ",',
        '    "core_beliefs": ["belief 1", "belief 2", "belief 3"],',
        '    "key_disagreement": "One sentence on what most sets this group apart from the other groups"',
        "  },",
        "  ...",
        "]",
        "",
        "STRICT REQUIREMENTS:",
        "- Every label MUST be unique — no word may appear in more than one group label.",
        "- Do not reuse adjectives, political categories, or descriptors across group descriptions.",
        "- Each description must reference HOW this group differs from the others, not just describe them in isolation.",
        "- If two groups share a belief, focus on the belief or stance that ONLY this group holds.",
    ]

    return "\n".join(lines)


def call_openai(api_key: str, prompt: str) -> list[dict]:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.7,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a political analyst. Respond with valid JSON only. "
                    "Your response must be a JSON object with a single key 'groups' containing an array."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )
    raw = response.choices[0].message.content
    parsed = json.loads(raw)

    # Model returns {"groups": [...]} or directly a list
    if isinstance(parsed, list):
        return parsed
    if "groups" in parsed:
        return parsed["groups"]
    # Fallback: look for any list value in the top-level dict
    for v in parsed.values():
        if isinstance(v, list):
            return v
    return []


def generate_summaries(
    api_key: str,
    result: AnalysisResult,
) -> list[GroupSummaryRead]:
    prompt = build_prompt(result.clusters, result.statements, result.k)
    groups = call_openai(api_key, prompt)

    # Index returned objects by their "group" field (1-based) or by position
    by_position: dict[int, dict] = {}
    for i, g in enumerate(groups):
        group_num = int(g.get("group", i + 1))
        by_position[group_num] = g

    summaries: list[GroupSummaryRead] = []
    for cluster in result.clusters:
        cluster_num = cluster.k + 1  # 1-based
        data = by_position.get(cluster_num, {})

        core_beliefs = data.get("core_beliefs", [])
        if isinstance(core_beliefs, str):
            core_beliefs = [core_beliefs]
        core_beliefs = [str(b) for b in core_beliefs[:5]]

        summaries.append(
            GroupSummaryRead(
                cluster_idx=cluster.k,
                label=str(data.get("label", f"Group {cluster_num}")),
                description=str(data.get("description", "")),
                core_beliefs=core_beliefs,
                key_disagreement=str(data.get("key_disagreement", "")),
            )
        )
    return summaries
