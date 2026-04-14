from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Setting
from ..schemas import OpenAIKeyStatus, OpenAIKeySave

router = APIRouter(prefix="/settings", tags=["settings"])

OPENAI_KEY_NAME = "openai_api_key"


@router.get("/openai-key", response_model=OpenAIKeyStatus)
def get_openai_key_status(db: Session = Depends(get_db)):
    row = db.query(Setting).filter(Setting.key == OPENAI_KEY_NAME).first()
    return OpenAIKeyStatus(configured=row is not None and bool(row.value))


@router.post("/openai-key", response_model=OpenAIKeyStatus)
def save_openai_key(payload: OpenAIKeySave, db: Session = Depends(get_db)):
    row = db.query(Setting).filter(Setting.key == OPENAI_KEY_NAME).first()
    if row:
        row.value = payload.key.strip()
    else:
        db.add(Setting(key=OPENAI_KEY_NAME, value=payload.key.strip()))
    db.commit()
    return OpenAIKeyStatus(configured=True)
