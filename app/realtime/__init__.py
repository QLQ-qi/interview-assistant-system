"""
实时通信模块 - WebSocket
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
import json
from typing import Dict, Set
from uuid import UUID

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 按session_id存储连接
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        """建立连接"""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        
        self.active_connections[session_id].add(websocket)
        logger.info(f"Client connected to session {session_id}")
    
    async def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        """断开连接"""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        
        logger.info(f"Client disconnected from session {session_id}")
    
    async def broadcast(self, session_id: str, message: dict) -> None:
        """广播消息到会话内的所有连接"""
        if session_id not in self.active_connections:
            return
        
        # 转换为JSON
        message_json = json.dumps(message)
        
        # 发送给所有连接
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending message: {e}")


# 全局连接管理器
manager = ConnectionManager()


@router.websocket("/ws/meeting/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket端点 - 接收和发送实时数据
    
    客户端连接到: ws://localhost:8000/ws/meeting/<session_id>
    """
    await manager.connect(session_id, websocket)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            
            message = json.loads(data)
            
            if message.get('type') == 'ping':
                # 响应心跳
                await websocket.send_text(json.dumps({"type": "pong"}))
            else:
                logger.debug(f"Received message from client: {message}")
    
    except WebSocketDisconnect:
        await manager.disconnect(session_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        await manager.disconnect(session_id, websocket)


# 导出路由
websocket_router = router
