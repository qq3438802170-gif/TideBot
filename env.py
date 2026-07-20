import json
from typing import List, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    TideBot 全局强类型环境配置加载器
    基于 Pydantic v2 与 Pydantic-Settings 实现，在服务拉起阶段强制校验关键密钥
    """
    PROJECT_NAME: str = "TideBot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # 安全配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 默认 7 天

    # 跨域配置
    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            if isinstance(v, str):
                return json.loads(v)
            return v
        raise ValueError(f"CORS 配置异常格式: {v}")

    # 数据源连接
    DATABASE_URL: str = "sqlite+aiosqlite:///./tidebot.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # 外部 IM 桥接专属密匙
    OPENCLAW_API_URL: str = "http://localhost:8090"
    OPENCLAW_SECRET: str = ""

    # 读取规则配置
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()