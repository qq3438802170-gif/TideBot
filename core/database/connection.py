from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.config_manager import ConfigManager
import logging

logger = logging.getLogger("TideBot")

# 获取数据库连接 URL
db_url = ConfigManager().env.database_url

# 创建异步 SQLAlchemy 引擎
engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    pool_pre_ping=True
)

# 创建异步 Session 工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db_session():
    """
    FastAPI 依赖函数：提供异步数据库会话，并在请求结束时安全关闭
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()