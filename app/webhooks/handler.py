"""
Webhook处理器 - 接收腾讯会议推送
"""
import json
import hmac
import hashlib
import logging
from typing import Dict, Any
from datetime import datetime

from app.config import settings
from app.database.models import TranscriptionRecord, MeetingSession, SessionStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

logger = logging.getLogger(__name__)


class WebhookHandler:
    """腾讯会议Webhook处理器"""
    
    @staticmethod
    def verify_signature(
        token: str,
        timestamp: str,
        nonce: str,
        body: str
    ) -> str:
        """
        验证Webhook签名 (HMAC-SHA256)
        
        Args:
            token: Webhook token
            timestamp: 时间戳
            nonce: 随机数
            body: 请求体
            
        Returns:
            计算的签名
        """
        # 构建签名源字符串
        sign_str = f"{timestamp}{nonce}{body}"
        
        # 计算HMAC-SHA256
        signature = hmac.new(
            token.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    @staticmethod
    async def handle_meeting_started(
        payload: Dict[str, Any],
        db: AsyncSession
    ) -> None:
        """
        处理会议开始事件
        
        Args:
            payload: 事件数据
            db: 数据库会话
        """
        meeting_id = payload.get('meeting_id')
        interviewer_id = payload.get('interviewer_id')
        candidate_id = payload.get('candidate_id')
        position_id = payload.get('position_id')
        
        logger.info(f"Meeting started: {meeting_id}")
        
        # 创建会议会话
        session = MeetingSession(
            meeting_id=meeting_id,
            interviewer_id=interviewer_id,
            candidate_id=candidate_id,
            position_id=position_id,
            status=SessionStatus.STARTED,
            started_at=datetime.utcnow()
        )
        
        db.add(session)
        await db.commit()
        
        logger.info(f"Meeting session created: {session.id}")
    
    @staticmethod
    async def handle_transcription(
        payload: Dict[str, Any],
        db: AsyncSession
    ) -> None:
        """
        处理实时转写事件
        
        Args:
            payload: 事件数据
            db: 数据库会话
        """
        meeting_id = payload.get('meeting_id')
        participant_id = payload.get('participant_id')
        text = payload.get('text')
        timestamp = payload.get('timestamp')
        confidence = payload.get('confidence', 1.0)
        speaker_name = payload.get('speaker_name', '')
        sequence_number = payload.get('sequence_number', 0)
        
        logger.info(f"Transcription received: {meeting_id} - {text[:50]}...")
        
        # 获取对应的会议会话
        result = await db.execute(
            select(MeetingSession).where(
                MeetingSession.meeting_id == meeting_id
            )
        )
        session = result.scalars().first()
        
        if not session:
            logger.warning(f"Session not found for meeting: {meeting_id}")
            return
        
        # 保存转写记录
        record = TranscriptionRecord(
            session_id=session.id,
            speaker_type='interviewer' if participant_id == session.interviewer_id else 'candidate',
            text=text,
            confidence=confidence,
            sequence_number=sequence_number,
            created_at=datetime.fromisoformat(timestamp) if timestamp else datetime.utcnow()
        )
        
        db.add(record)
        await db.commit()
        
        logger.info(f"Transcription record saved: {record.id}")
        
        # TODO: 触发知识库查询和LLM推理
    
    @staticmethod
    async def handle_recording_completed(
        payload: Dict[str, Any],
        db: AsyncSession
    ) -> None:
        """
        处理录制完成事件
        
        Args:
            payload: 事件数据
            db: 数据库会话
        """
        meeting_id = payload.get('meeting_id')
        recording_url = payload.get('recording_url')
        
        logger.info(f"Recording completed: {meeting_id}")
        
        # 更新会议会话状态
        await db.execute(
            update(MeetingSession)
            .where(MeetingSession.meeting_id == meeting_id)
            .values(status=SessionStatus.ENDED)
        )
        await db.commit()
        
        # TODO: 触发录音转写和知识库导入
        logger.info(f"Recording stored: {recording_url}")
    
    @staticmethod
    async def process_event(
        event_type: str,
        payload: Dict[str, Any],
        db: AsyncSession
    ) -> None:
        """
        处理Webhook事件
        
        Args:
            event_type: 事件类型
            payload: 事件数据
            db: 数据库会话
        """
        try:
            if event_type == 'meeting.started':
                await WebhookHandler.handle_meeting_started(payload, db)
            elif event_type == 'transcription.received':
                await WebhookHandler.handle_transcription(payload, db)
            elif event_type == 'recording.completed':
                await WebhookHandler.handle_recording_completed(payload, db)
            else:
                logger.warning(f"Unknown event type: {event_type}")
        except Exception as e:
            logger.error(f"Error processing event {event_type}: {e}", exc_info=True)
            raise
