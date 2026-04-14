from datetime import datetime
from sqlalchemy import (
    Boolean, CheckConstraint, Column, DateTime, ForeignKey,
    Integer, String, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    statements = relationship("Statement", back_populates="survey", cascade="all, delete-orphan")
    participants = relationship("Participant", back_populates="survey", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="survey", cascade="all, delete-orphan")


class Statement(Base):
    __tablename__ = "statements"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    survey = relationship("Survey", back_populates="statements")
    responses = relationship("Response", back_populates="statement", cascade="all, delete-orphan")


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    label = Column(String(255), nullable=True)

    survey = relationship("Survey", back_populates="participants")
    responses = relationship("Response", back_populates="participant", cascade="all, delete-orphan")


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False)
    participant_id = Column(Integer, ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)
    statement_id = Column(Integer, ForeignKey("statements.id", ondelete="CASCADE"), nullable=False)
    vote = Column(String(10), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("vote IN ('agree', 'disagree', 'pass')", name="vote_values"),
        UniqueConstraint("participant_id", "statement_id", name="uq_participant_statement"),
    )

    survey = relationship("Survey", back_populates="responses")
    participant = relationship("Participant", back_populates="responses")
    statement = relationship("Statement", back_populates="responses")


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String(255), primary_key=True)
    value = Column(Text, nullable=False)


class GroupSummary(Base):
    __tablename__ = "group_summaries"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False)
    k_groups = Column(Integer, nullable=False)
    cluster_idx = Column(Integer, nullable=False)
    label = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    core_beliefs = Column(Text, nullable=False)  # JSON array as string
    key_disagreement = Column(Text, nullable=False)
    generated_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("survey_id", "k_groups", "cluster_idx", name="uq_survey_k_cluster"),
    )
