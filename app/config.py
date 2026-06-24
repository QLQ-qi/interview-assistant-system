"""
应用配置管理
"""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用设置"""
    
    # 基本设置
    APP_NAME: str = "Interview Assistant System"
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # 数据库设置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/interview_db"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # 腾讯会议设置
    TENCENT_MEETING_APP_ID: str = os.getenv("TENCENT_MEETING_APP_ID", "")
    TENCENT_MEETING_APP_SECRET: str = os.getenv("TENCENT_MEETING_APP_SECRET", "")
    TENCENT_MEETING_WEBHOOK_TOKEN: str = os.getenv("TENCENT_MEETING_WEBHOOK_TOKEN", "")
    TENCENT_MEETING_WEBHOOK_ENCODING_AES_KEY: str = os.getenv(
        "TENCENT_MEETING_WEBHOOK_ENCODING_AES_KEY", ""
    )
    
    # LLM设置
    LLM_API_URL: str = os.getenv("LLM_API_URL", "http://localhost:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen:latest")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    LLM_TOP_P: float = float(os.getenv("LLM_TOP_P", "0.9"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1000"))
    
    # 向量模型设置
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
    EMBEDDING_DEVICE: str = os.getenv("EMBEDDING_DEVICE", "cuda")
    
    # Webhook设置
    WEBHOOK_TIMEOUT: int = int(os.getenv("WEBHOOK_TIMEOUT", "30"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    WEBHOOK_RETRY_TIMES: int = int(os.getenv("WEBHOOK_RETRY_TIMES", "3"))
    
    # CORS设置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    
    # 知识库设置
    KB_VECTOR_DIM: int = 1024  # BGE-M3的向量维度
    KB_TOP_K: int = 5  # 返回top-k结果
    KB_SIMILARITY_THRESHOLD: float = 0.5  # 相似度阈值
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


# 全局设置实例
settings = Settings()
