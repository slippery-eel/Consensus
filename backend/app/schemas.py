from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict


# ── Statement ────────────────────────────────────────────────────────────────

class StatementCreate(BaseModel):
    text: str


class StatementUpdate(BaseModel):
    text: Optional[str] = None
    is_active: Optional[bool] = None


class StatementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    survey_id: int
    text: str
    is_active: bool
    created_at: datetime


# ── Survey ───────────────────────────────────────────────────────────────────

class SurveyCreate(BaseModel):
    title: str
    description: Optional[str] = None


class SurveyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    created_at: datetime
    statements: list[StatementRead] = []


class SurveyListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    created_at: datetime


# ── Participant ───────────────────────────────────────────────────────────────

class ParticipantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    survey_id: int
    created_at: datetime


# ── Response ──────────────────────────────────────────────────────────────────

class ResponseCreate(BaseModel):
    statement_id: int
    vote: Literal["agree", "disagree", "pass"]


class ResponseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    survey_id: int
    participant_id: int
    statement_id: int
    vote: str
    created_at: datetime


# ── Analysis ──────────────────────────────────────────────────────────────────

class ParticipantPoint(BaseModel):
    id: int
    pca_x: float
    pca_y: float
    cluster: int


class StatementStat(BaseModel):
    id: int
    text: str
    agree_rate: float
    disagree_rate: float
    pass_rate: float
    agree_count: int
    disagree_count: int
    pass_count: int
    is_consensus: bool
    is_divisive: bool
    cluster_score: float


class ClusterSummary(BaseModel):
    k: int
    size: int
    mean_votes: dict[int, float]


class AnalysisResult(BaseModel):
    participants: list[ParticipantPoint]
    statements: list[StatementStat]
    clusters: list[ClusterSummary]
    pca_variance_explained: list[float]
    k: int
    n_participants: int
    n_statements: int


# ── Summaries ─────────────────────────────────────────────────────────────────

class GroupSummaryRead(BaseModel):
    cluster_idx: int
    label: str
    description: str
    core_beliefs: list[str]
    key_disagreement: str


class SummarizeResult(BaseModel):
    summaries: list[GroupSummaryRead]
    cached: bool


# ── Settings ──────────────────────────────────────────────────────────────────

class OpenAIKeyStatus(BaseModel):
    configured: bool


class OpenAIKeySave(BaseModel):
    key: str
