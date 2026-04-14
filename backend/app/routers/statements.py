from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Statement, Survey
from ..schemas import StatementCreate, StatementRead, StatementUpdate

router = APIRouter(tags=["statements"])


@router.post("/surveys/{survey_id}/statements", response_model=StatementRead, status_code=201)
def add_statement(survey_id: int, payload: StatementCreate, db: Session = Depends(get_db)):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    stmt = Statement(survey_id=survey_id, text=payload.text)
    db.add(stmt)
    db.commit()
    db.refresh(stmt)
    return stmt


@router.patch("/statements/{statement_id}", response_model=StatementRead)
def update_statement(
    statement_id: int, payload: StatementUpdate, db: Session = Depends(get_db)
):
    stmt = db.query(Statement).filter(Statement.id == statement_id).first()
    if not stmt:
        raise HTTPException(status_code=404, detail="Statement not found")
    if payload.text is not None:
        stmt.text = payload.text
    if payload.is_active is not None:
        stmt.is_active = payload.is_active
    db.commit()
    db.refresh(stmt)
    return stmt


@router.delete("/statements/{statement_id}", status_code=204)
def delete_statement(statement_id: int, db: Session = Depends(get_db)):
    stmt = db.query(Statement).filter(Statement.id == statement_id).first()
    if not stmt:
        raise HTTPException(status_code=404, detail="Statement not found")
    db.delete(stmt)
    db.commit()
