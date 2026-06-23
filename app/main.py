"""
FastAPI 主应用程序入口
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db, engine
from app.webhooks import router as webhook_router
from app.realtime import websocket_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    logger.info("Initializing application...")
    await init_db()
    logger.info("Application started successfully")
    
    yield
    
    # 关闭
    logger.info("Shutting down application...")
    await engine.dispose()
    logger.info("Application shutdown complete")


# 创建FastAPI应用
app = FastAPI(
    title="面试辅助系统 API",
    description="基于腾讯会议 + 本地LLM的实时面试辅助系统",
    version="0.1.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 路由注册
app.include_router(webhook_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(websocket_router, tags=["realtime"])


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "interview-assistant-system",
        "version": "0.1.0"
    }


# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
