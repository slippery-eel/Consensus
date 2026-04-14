from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..analytics import run_analysis
from ..database import get_db
from ..schemas import AnalysisResult

router = APIRouter(tags=["analysis"])


@router.post("/surveys/{survey_id}/analyze", response_model=AnalysisResult)
def analyze_survey(survey_id: int, k: int = 2, db: Session = Depends(get_db)):
    if k < 2 or k > 10:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="k must be between 2 and 10")
    return run_analysis(db, survey_id, k)
