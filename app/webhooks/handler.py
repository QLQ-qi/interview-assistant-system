"""Webhook handler - receives Tencent Meeting events and processes them"""
import json
import hmac
import hashlib
import logging
from typing import Dict, Any
from datetime import datetime

from app.config import settings
from app.database.models import MeetingSession, SessionStatus
from app.transcription.processor import TranscriptionProcessor
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

logger = logging.getLogger(__name__)


class WebhookHandler:
    """Tencent Meeting Webhook event handler"""

    _processor = TranscriptionProcessor()

    @staticmethod
    def verify_signature(
        token: str,
        timestamp: str,
        nonce: str,
        body: str
    ) -> str:
        """Verify Webhook signature using HMAC-SHA256"""
        sign_str = f"{timestamp}{nonce}{body}"
        return hmac.new(
            token.encode("utf-8"),
            sign_str.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    async def handle_meeting_started(
        payload: Dict[str, Any],
        db: AsyncSession,
    ) -> None:
        """Handle meeting.started event - create a new meeting session"""
        meeting_id = payload.get("meeting_id", "")
        interviewer_id = payload.get("interviewer_id", "")
        candidate_id = payload.get("candidate_id", "")
        position_id = payload.get("position_id", "")

        logger.info(f"Meeting started: {meeting_id}")

        session = MeetingSession(
            meeting_id=meeting_id,
            interviewer_id=interviewer_id,
            candidate_id=candidate_id,
            position_id=position_id,
            status=SessionStatus.STARTED,
            started_at=datetime.utcnow(),
        )
        db.add(session)
        await db.commit()

        logger.info(f"Meeting session created: {session.id}")

    @staticmethod
    async def handle_transcription(
        payload: Dict[str, Any],
        db: AsyncSession,
    ) -> None:
        """Process transcription via the full pipeline: save -> LLM -> WebSocket"""
        meeting_id = payload.get("meeting_id", "")
        participant_id = payload.get("participant_id", "")
        text = payload.get("text", "")
        timestamp = payload.get("timestamp")
        speaker_name = payload.get("speaker_name", "")

        await WebhookHandler._processor.process(
            db=db,
            meeting_id=meeting_id,
            participant_id=participant_id,
            text=text,
            timestamp=timestamp,
            speaker_name=speaker_name,
        )

    @staticmethod
    async def handle_recording_completed(
        payload: Dict[str, Any],
        db: AsyncSession,
    ) -> None:
        """Handle recording.completed event - update session status"""
        meeting_id = payload.get("meeting_id", "")
        recording_url = payload.get("recording_url", "")

        logger.info(f"Recording completed: {meeting_id}")

        await db.execute(
            update(MeetingSession)
            .where(MeetingSession.meeting_id == meeting_id)
            .values(status=SessionStatus.ENDED)
        )
        await db.commit()

        logger.info(f"Recording stored: {recording_url}")

    @staticmethod
    async def process_event(
        event_type: str,
        payload: Dict[str, Any],
        db: AsyncSession,
    ) -> None:
        """Route webhook events to the appropriate handler"""
        try:
            if event_type == "meeting.started":
                await WebhookHandler.handle_meeting_started(payload, db)
            elif event_type == "transcription.received":
                await WebhookHandler.handle_transcription(payload, db)
            elif event_type == "recording.completed":
                await WebhookHandler.handle_recording_completed(payload, db)
            else:
                logger.warning(f"Unknown event type: {event_type}")
        except Exception as e:
            logger.error(f"Error processing event {event_type}: {e}", exc_info=True)
            raise
