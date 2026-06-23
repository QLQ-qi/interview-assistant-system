"""
转写相关的数据模型
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum


class SpeakerType(str, enum.Enum):
    """说话人类型"""
    INTERVIEWER = "interviewer"
    CANDIDATE = "candidate"


class SessionStatus(str, enum.Enum):
    """会议状态"""
    WAITING = "waiting"
    STARTED = "started"
    ENDED = "ended"


class MeetingSession(Base):
    """会议会话表"""
    __tablename__ = "meeting_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    meeting_id = Column(String(255), unique=True, nullable=False, index=True)
    interviewer_id = Column(String(255), nullable=False)
    candidate_id = Column(String(255), nullable=False)
    position_id = Column(String(255), nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.WAITING, nullable=False)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TranscriptionRecord(Base):
    """转写记录表"""
    __tablename__ = "transcription_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('meeting_sessions.id'), nullable=False, index=True)
    speaker_type = Column(Enum(SpeakerType), nullable=False)
    text = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    sequence_number = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class TranscriptionHint(Base):
    """转写提示表 - 存储LLM生成的提醒"""
    __tablename__ = "transcription_hints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    record_id = Column(Integer, ForeignKey('transcription_records.id'), nullable=False, index=True)
    hint_type = Column(String(50), nullable=False)  # 'standard_talk', 'case_reference', 'warning'
    content = Column(Text, nullable=False)
    confidence = Column(Float, default=0.8, nullable=False)
    source_type = Column(String(50), nullable=False)  # 'knowledge_base', 'llm_generated'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class FeedbackRecord(Base):
    """反馈记录表 - 用于后续沉淀"""
    __tablename__ = "feedback_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    hint_id = Column(UUID(as_uuid=True), ForeignKey('transcription_hints.id'), nullable=False, index=True)
    interviewer_feedback = Column(String(255), nullable=True)
    useful = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
