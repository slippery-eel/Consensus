import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..analytics import run_analysis
from ..database import get_db
from ..models import GroupSummary, Setting
from ..schemas import GroupSummaryRead, SummarizeResult
from ..summarizer import generate_summaries

router = APIRouter(tags=["summaries"])

OPENAI_KEY_NAME = "openai_api_key"


def _get_api_key(db: Session) -> str:
    row = db.query(Setting).filter(Setting.key == OPENAI_KEY_NAME).first()
    if not row or not row.value:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key not configured. Add it in Admin → Settings.",
        )
    return row.value


def _load_cached(db: Session, survey_id: int, k: int) -> list[GroupSummaryRead] | None:
    rows = (
        db.query(GroupSummary)
        .filter(GroupSummary.survey_id == survey_id, GroupSummary.k_groups == k)
        .order_by(GroupSummary.cluster_idx)
        .all()
    )
    if not rows:
        return None
    return [
        GroupSummaryRead(
            cluster_idx=r.cluster_idx,
            label=r.label,
            description=r.description,
            core_beliefs=json.loads(r.core_beliefs),
            key_disagreement=r.key_disagreement,
        )
        for r in rows
    ]


def _save_summaries(db: Session, survey_id: int, k: int, summaries: list[GroupSummaryRead]):
    for s in summaries:
        existing = (
            db.query(GroupSummary)
            .filter(
                GroupSummary.survey_id == survey_id,
                GroupSummary.k_groups == k,
                GroupSummary.cluster_idx == s.cluster_idx,
            )
            .first()
        )
        if existing:
            existing.label = s.label
            existing.description = s.description
            existing.core_beliefs = json.dumps(s.core_beliefs)
            existing.key_disagreement = s.key_disagreement
        else:
            db.add(
                GroupSummary(
                    survey_id=survey_id,
                    k_groups=k,
                    cluster_idx=s.cluster_idx,
                    label=s.label,
                    description=s.description,
                    core_beliefs=json.dumps(s.core_beliefs),
                    key_disagreement=s.key_disagreement,
                )
            )
    db.commit()


@router.get("/surveys/{survey_id}/summaries", response_model=SummarizeResult)
def get_summaries(survey_id: int, k: int = 2, db: Session = Depends(get_db)):
    cached = _load_cached(db, survey_id, k)
    if cached:
        return SummarizeResult(summaries=cached, cached=True)
    return SummarizeResult(summaries=[], cached=False)


@router.post("/surveys/{survey_id}/summarize", response_model=SummarizeResult)
def summarize_survey(
    survey_id: int,
    k: int = 2,
    force: bool = False,
    db: Session = Depends(get_db),
):
    api_key = _get_api_key(db)

    if not force:
        cached = _load_cached(db, survey_id, k)
        if cached:
            return SummarizeResult(summaries=cached, cached=True)

    # Run clustering analysis to get current data
    result = run_analysis(db, survey_id, k)

    # Call OpenAI for each cluster
    try:
        summaries = generate_summaries(api_key, result)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"OpenAI error: {str(e)}")

    _save_summaries(db, survey_id, k, summaries)
    return SummarizeResult(summaries=summaries, cached=False)
