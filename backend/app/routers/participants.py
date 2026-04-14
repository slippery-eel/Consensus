from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Participant, Survey
from ..schemas import ParticipantRead

router = APIRouter(tags=["participants"])


@router.post("/surveys/{survey_id}/sessions", response_model=ParticipantRead, status_code=201)
def create_session(survey_id: int, db: Session = Depends(get_db)):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    participant = Participant(survey_id=survey_id)
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant
