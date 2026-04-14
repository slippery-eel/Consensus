from __future__ import annotations

import json
from openai import OpenAI

from .schemas import AnalysisResult, ClusterSummary, GroupSummaryRead, StatementStat


def build_prompt(
    cluster: ClusterSummary,
    all_clusters: list[ClusterSummary],
    statements: list[StatementStat],
    k: int,
) -> str:
    idx = cluster.k
    size = cluster.size

    # Top distinguishing statements (highest cluster_score = most group-separating)
    distinguishing = sorted(statements, key=lambda s: s.cluster_score, reverse=True)[:10]

    # This cluster's strong agreements and disagreements
    mean = cluster.mean_votes
    strong_agree = sorted(
        [s for s in statements if mean.get(s.id, 0) > 0.4],
        key=lambda s: mean.get(s.id, 0),
        reverse=True,
    )[:6]
    strong_disagree = sorted(
        [s for s in statements if mean.get(s.id, 0) < -0.4],
        key=lambda s: mean.get(s.id, 0),
    )[:6]

    # Cross-group consensus
    consensus = [s for s in statements if s.is_consensus]

    def fmt_stmt(s: StatementStat) -> str:
        v = mean.get(s.id, 0)
        return f'  - "{s.text}" → this group avg: {v:+.2f}'

    lines = [
        "You are analyzing results from a structured political opinion survey.",
        "",
        "Participants voted Agree (+1), Disagree (-1), or Pass (0) on 30 statements.",
        f"They were grouped by voting similarity using PCA + k-means into {k} groups.",
        "",
        f"This is GROUP {idx + 1} of {k} ({size} participant{'s' if size != 1 else ''}).",
        "",
        "STATEMENTS THAT MOST DISTINGUISH THIS GROUP FROM OTHERS",
        "(sorted by how strongly this statement separates groups):",
    ]
    for s in distinguishing:
        lines.append(fmt_stmt(s))

    if strong_agree:
        lines += ["", "THIS GROUP'S STRONGEST AGREEMENTS (avg > 0.4):"]
        for s in strong_agree:
            lines.append(fmt_stmt(s))

    if strong_disagree:
        lines += ["", "THIS GROUP'S STRONGEST DISAGREEMENTS (avg < -0.4):"]
        for s in strong_disagree:
            lines.append(fmt_stmt(s))

    if consensus:
        lines += ["", "STATEMENTS THE WHOLE SURVEY BROADLY AGREED ON (cross-group consensus):"]
        for s in consensus:
            lines.append(f'  - "{s.text}"')

    lines += [
        "",
        "Based on the above, provide a JSON object describing this group:",
        '{',
        '  "label": "2-4 word name (e.g. Progressive Left, Libertarian-Leaning, Religious Conservative)",',
        '  "description": "2-3 sentences on this group\'s political orientation and worldview",',
        '  "core_beliefs": ["belief 1", "belief 2", "belief 3"],',
        '  "key_disagreement": "One sentence on what most sets this group apart or what they\'d push back on hardest"',
        '}',
    ]

    return "\n".join(lines)


def call_openai(api_key: str, prompt: str) -> dict:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.4,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a political analyst. Always respond with valid JSON only.",
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
    for cluster in result.clusters:
        prompt = build_prompt(cluster, result.clusters, result.statements, result.k)
        data = call_openai(api_key, prompt)

        # Normalise — model may sometimes return extra/missing fields
        core_beliefs = data.get("core_beliefs", [])
        if isinstance(core_beliefs, str):
            core_beliefs = [core_beliefs]
        core_beliefs = [str(b) for b in core_beliefs[:5]]

        summaries.append(
            GroupSummaryRead(
                cluster_idx=cluster.k,
                label=str(data.get("label", f"Group {cluster.k + 1}")),
                description=str(data.get("description", "")),
                core_beliefs=core_beliefs,
                key_disagreement=str(data.get("key_disagreement", "")),
            )
        )
    return summaries
