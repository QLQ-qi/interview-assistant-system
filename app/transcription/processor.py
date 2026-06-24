"""Transcription Processor - manages the transcription-to-hint pipeline"""
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import TranscriptionRecord, MeetingSession, TranscriptionHint
from app.llm.service import get_llm
from app.realtime import manager

logger = logging.getLogger(__name__)


class TranscriptionProcessor:
    """Processes incoming transcription and triggers LLM analysis + WebSocket push"""

    def __init__(self):
        self._history_cache: dict[str, list[dict]] = {}

    async def process(
        self,
        db: AsyncSession,
        meeting_id: str,
        participant_id: str,
        text: str,
        timestamp: Optional[str] = None,
        speaker_name: str = "",
    ) -> None:
        """Process a transcription: save, analyze with LLM, push hints via WebSocket.
        
        Args:
            db: Database session
            meeting_id: The meeting ID
            participant_id: Who spoke
            text: The transcription text
            timestamp: ISO timestamp string
            speaker_name: Display name of speaker
        """
        # 1. Get the meeting session
        result = await db.execute(
            select(MeetingSession).where(MeetingSession.meeting_id == meeting_id)
        )
        session = result.scalars().first()
        if not session:
            logger.warning(f"Session not found for meeting: {meeting_id}")
            return

        session_id_str = meeting_id

        # 2. Determine speaker type
        speaker = "interviewer" if participant_id == session.interviewer_id else "candidate"

        # 3. Save transcription to DB
        record = TranscriptionRecord(
            session_id=session.id,
            speaker_type=speaker,
            text=text,
            confidence=1.0,
            sequence_number=0,
            created_at=datetime.fromisoformat(timestamp) if timestamp else datetime.utcnow(),
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)

        logger.info(f"Transcription saved: {record.id} ({speaker})")

        # 4. Push transcription to WebSocket clients
        ws_message = {
            "type": "transcription",
            "session_id": session_id_str,
            "text": text,
            "speaker": speaker,
            "timestamp": record.created_at.isoformat(),
        }
        await manager.broadcast(session_id_str, ws_message)

        # 5. Update history cache
        if session_id_str not in self._history_cache:
            self._history_cache[session_id_str] = []
        self._history_cache[session_id_str].append({
            "speaker": speaker,
            "text": text,
            "timestamp": record.created_at.isoformat(),
        })
        # Keep only last 20 entries
        if len(self._history_cache[session_id_str]) > 20:
            self._history_cache[session_id_str] = self._history_cache[session_id_str][-20:]

        # 6. Run LLM analysis
        llm = get_llm()
        try:
            hints = await llm.analyze_transcription(
                history=self._history_cache[session_id_str][:-1],  # exclude current
                speaker=speaker,
                text=text,
                session_id=session_id_str,
            )
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            hints = []

        # 7. Process and push hints
        for hint_data in hints:
            hint_type = hint_data.get("hint_type", "standard_talk")
            content = hint_data.get("content", "")
            confidence = hint_data.get("confidence", 0.5)

            # Save hint to DB
            hint = TranscriptionHint(
                record_id=record.id,
                hint_type=hint_type,
                content=content,
                confidence=confidence,
                source_type="llm_generated",
                created_at=datetime.utcnow(),
            )
            db.add(hint)

            # Push hint via WebSocket
            hint_message = {
                "type": "hint",
                "session_id": session_id_str,
                "hint": content,
                "hint_type": hint_type,
                "confidence": confidence,
            }
            await manager.broadcast(session_id_str, hint_message)

        await db.commit()
        logger.info(f"Generated {len(hints)} hints for session {session_id_str}")
