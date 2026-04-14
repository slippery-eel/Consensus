from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Survey
from ..schemas import SurveyCreate, SurveyListItem, SurveyRead

router = APIRouter(prefix="/surveys", tags=["surveys"])


@router.get("", response_model=list[SurveyListItem])
def list_surveys(db: Session = Depends(get_db)):
    return db.query(Survey).order_by(Survey.created_at.desc()).all()


@router.post("", response_model=SurveyRead, status_code=201)
def create_survey(payload: SurveyCreate, db: Session = Depends(get_db)):
    survey = Survey(title=payload.title, description=payload.description)
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return survey


@router.get("/{survey_id}", response_model=SurveyRead)
def get_survey(survey_id: int, db: Session = Depends(get_db)):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    return survey
