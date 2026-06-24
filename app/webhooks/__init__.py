"""
Webhook模块
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import json
from datetime import datetime

from app.config import settings
from app.database import get_db
from pydantic import BaseModel
from app.webhooks.handler import WebhookHandler

logger = logging.getLogger(__name__)

router = APIRouter()





class SimulateTranscription(BaseModel):
    """Request body for transcription simulation"""
    meeting_id: str
    participant_id: str
    text: str
    timestamp: str = ""
    speaker_name: str = ""


@router.post("/simulate/transcription")
async def simulate_transcription(
    payload: SimulateTranscription,
    db: AsyncSession = Depends(get_db),
):
    """Simulate a transcription event for testing without Tencent Meeting.
    
    Useful for development and demo. Creates a meeting session if needed
    and processes the transcription through the full LLM pipeline.
    """
    from app.database.models import MeetingSession
    from sqlalchemy import select

    # Check if session exists, create one if not
    result = await db.execute(
        select(MeetingSession).where(MeetingSession.meeting_id == payload.meeting_id)
    )
    session = result.scalars().first()
    if not session:
        session = MeetingSession(
            meeting_id=payload.meeting_id,
            interviewer_id="interviewer-001",
            candidate_id="candidate-001",
            position_id="pos-001",
            status="started",
            started_at=datetime.utcnow(),
        )
        db.add(session)
        await db.commit()

    # Process via the standard pipeline
    from app.webhooks.handler import WebhookHandler
    event_payload = {
        "meeting_id": payload.meeting_id,
        "participant_id": payload.participant_id,
        "text": payload.text,
        "timestamp": payload.timestamp or datetime.utcnow().isoformat(),
        "speaker_name": payload.speaker_name,
    }
    await WebhookHandler.handle_transcription(event_payload, db)

    return {"status": "processed", "meeting_id": payload.meeting_id}

@router.get("/tencent-meeting")
async def webhook_verify(request: Request):
    """
    Webhook URL验证 (GET请求)
    
    腾讯会议平台会以GET方式验证URL有效性，需要返回echo_str验签
    """
    # 从查询参数获取verify_token
    echo_str = request.query_params.get('echo_str', '')
    
    if echo_str:
        # 直接返回echo_str用于验证
        return {"echo_str": echo_str}
    
    return {"status": "ok"}


@router.post("/tencent-meeting")
async def webhook_receive(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    接收腾讯会议Webhook推送 (POST请求)
    
    验证签名并处理事件
    """
    try:
        # 获取请求头
        token = settings.TENCENT_MEETING_WEBHOOK_TOKEN
        timestamp = request.headers.get('X-Timestamp', '')
        nonce = request.headers.get('X-Nonce', '')
        signature = request.headers.get('X-Signature', '')
        
        # 获取请求体
        body = await request.body()
        body_str = body.decode('utf-8')
        
        # 验证签名
        expected_signature = WebhookHandler.verify_signature(
            token, timestamp, nonce, body_str
        )
        
        if signature != expected_signature:
            logger.warning(f"Invalid signature: {signature} != {expected_signature}")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # 解析JSON
        payload = json.loads(body_str)
        
        # 获取事件类型
        event_type = payload.get('event_type')
        event_data = payload.get('event_data', {})
        
        logger.info(f"Processing webhook event: {event_type}")
        
        # 异步处理事件
        await WebhookHandler.process_event(event_type, event_data, db)
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
