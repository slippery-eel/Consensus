from __future__ import annotations

import numpy as np
from fastapi import HTTPException
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from .models import Response, Statement
from .schemas import AnalysisResult, ClusterSummary, ParticipantPoint, StatementStat


def run_analysis(db: Session, survey_id: int, k: int) -> AnalysisResult:
    # ── Pull data ──────────────────────────────────────────────────────────────
    responses = (
        db.query(Response)
        .filter(Response.survey_id == survey_id)
        .all()
    )

    active_statements = (
        db.query(Statement)
        .filter(Statement.survey_id == survey_id, Statement.is_active == True)
        .order_by(Statement.id)
        .all()
    )

    if not responses:
        raise HTTPException(status_code=400, detail="No responses yet — collect some votes first.")

    if len(active_statements) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 active statements to analyse.")

    # ── Build index maps ───────────────────────────────────────────────────────
    stmt_ids = [s.id for s in active_statements]
    stmt_index = {sid: i for i, sid in enumerate(stmt_ids)}
    stmt_text = {s.id: s.text for s in active_statements}

    participant_ids_ordered: list[int] = []
    seen: set[int] = set()
    for r in responses:
        if r.participant_id not in seen:
            participant_ids_ordered.append(r.participant_id)
            seen.add(r.participant_id)

    n_p = len(participant_ids_ordered)
    n_s = len(stmt_ids)
    p_index = {pid: i for i, pid in enumerate(participant_ids_ordered)}

    if n_p < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 participants to analyse.")
    if k > n_p:
        raise HTTPException(
            status_code=400,
            detail=f"k={k} is larger than the number of participants ({n_p}). Choose a smaller k.",
        )

    # ── Fill matrix ────────────────────────────────────────────────────────────
    VOTE_MAP = {"agree": 1, "disagree": -1, "pass": 0}
    matrix = np.zeros((n_p, n_s), dtype=float)

    for r in responses:
        if r.statement_id not in stmt_index:
            continue  # skip responses to inactive statements
        pi = p_index[r.participant_id]
        si = stmt_index[r.statement_id]
        matrix[pi, si] = VOTE_MAP.get(r.vote, 0)

    # ── Zero-variance guard ────────────────────────────────────────────────────
    col_std = np.std(matrix, axis=0)
    nonzero_mask = col_std > 0
    matrix_for_scaling = matrix.copy()
    matrix_for_scaling[:, ~nonzero_mask] = 0.0  # will scale to 0 anyway

    # ── Standardize ───────────────────────────────────────────────────────────
    scaler = StandardScaler()
    if np.any(nonzero_mask):
        matrix_for_scaling[:, nonzero_mask] = scaler.fit_transform(
            matrix_for_scaling[:, nonzero_mask]
        )

    # ── PCA ───────────────────────────────────────────────────────────────────
    n_components = min(2, n_p, n_s)
    pca = PCA(n_components=n_components, random_state=42)
    pca_coords = pca.fit_transform(matrix_for_scaling)

    # Pad to 2 columns if only 1 component available
    if pca_coords.shape[1] < 2:
        pca_coords = np.hstack([pca_coords, np.zeros((n_p, 1))])
    variance_explained = pca.explained_variance_ratio_.tolist()
    if len(variance_explained) < 2:
        variance_explained.append(0.0)

    # ── KMeans ────────────────────────────────────────────────────────────────
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(pca_coords)

    # ── Statement stats ────────────────────────────────────────────────────────
    cluster_means: list[np.ndarray] = []
    for ki in range(k):
        mask = labels == ki
        cluster_means.append(matrix[mask].mean(axis=0) if mask.sum() > 0 else np.zeros(n_s))

    statement_stats: list[StatementStat] = []
    for si, sid in enumerate(stmt_ids):
        col = matrix[:, si]
        agree_count = int((col == 1).sum())
        disagree_count = int((col == -1).sum())
        pass_count = int((col == 0).sum())
        agree_rate = agree_count / n_p
        disagree_rate = disagree_count / n_p
        pass_rate = pass_count / n_p

        is_consensus = agree_rate >= 0.70 and disagree_rate <= 0.20
        is_divisive = (0.35 <= agree_rate <= 0.65) and (0.35 <= disagree_rate <= 0.65)

        # Cluster-distinguishing score: max pairwise diff of cluster means
        if k == 1:
            cluster_score = 0.0
        else:
            means_for_stmt = [cluster_means[ki][si] for ki in range(k)]
            cluster_score = float(
                max(
                    abs(means_for_stmt[a] - means_for_stmt[b])
                    for a in range(k)
                    for b in range(a + 1, k)
                )
            )

        statement_stats.append(
            StatementStat(
                id=sid,
                text=stmt_text[sid],
                agree_rate=round(agree_rate, 4),
                disagree_rate=round(disagree_rate, 4),
                pass_rate=round(pass_rate, 4),
                agree_count=agree_count,
                disagree_count=disagree_count,
                pass_count=pass_count,
                is_consensus=is_consensus,
                is_divisive=is_divisive,
                cluster_score=round(cluster_score, 4),
            )
        )

    # ── Cluster summaries ──────────────────────────────────────────────────────
    cluster_summaries: list[ClusterSummary] = []
    for ki in range(k):
        mask = labels == ki
        mean_votes = {
            stmt_ids[si]: round(float(cluster_means[ki][si]), 4)
            for si in range(n_s)
        }
        cluster_summaries.append(
            ClusterSummary(k=ki, size=int(mask.sum()), mean_votes=mean_votes)
        )

    # ── Participant points ─────────────────────────────────────────────────────
    participant_points = [
        ParticipantPoint(
            id=participant_ids_ordered[i],
            pca_x=round(float(pca_coords[i, 0]), 4),
            pca_y=round(float(pca_coords[i, 1]), 4),
            cluster=int(labels[i]),
        )
        for i in range(n_p)
    ]

    return AnalysisResult(
        participants=participant_points,
        statements=statement_stats,
        clusters=cluster_summaries,
        pca_variance_explained=[round(v, 4) for v in variance_explained],
        k=k,
        n_participants=n_p,
        n_statements=n_s,
    )
