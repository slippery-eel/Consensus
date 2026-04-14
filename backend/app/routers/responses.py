from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Participant, Response, Statement
from ..schemas import ResponseCreate, ResponseRead

router = APIRouter(tags=["responses"])


@router.post("/sessions/{participant_id}/responses", response_model=list[ResponseRead])
def submit_responses(
    participant_id: int,
    payload: list[ResponseCreate],
    db: Session = Depends(get_db),
):
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Session not found")

    results = []
    for item in payload:
        stmt = db.query(Statement).filter(Statement.id == item.statement_id).first()
        if not stmt:
            raise HTTPException(
                status_code=404, detail=f"Statement {item.statement_id} not found"
            )

        existing = (
            db.query(Response)
            .filter(
                Response.participant_id == participant_id,
                Response.statement_id == item.statement_id,
            )
            .first()
        )

        if existing:
            existing.vote = item.vote
            results.append(existing)
        else:
            response = Response(
                survey_id=participant.survey_id,
                participant_id=participant_id,
                statement_id=item.statement_id,
                vote=item.vote,
            )
            db.add(response)
            results.append(response)

    db.commit()
    for r in results:
        db.refresh(r)
    return results


@router.get("/surveys/{survey_id}/responses", response_model=list[ResponseRead])
def get_responses(survey_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Response)
        .filter(Response.survey_id == survey_id)
        .order_by(Response.participant_id, Response.statement_id)
        .all()
    )
