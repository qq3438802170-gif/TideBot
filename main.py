import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from env import settings
from api.middleware import TideBotMiddleware
from api.v1.auth import router as auth_router
from api.v1.bot import router as bot_router
from api.v1.channel import router as channel_router
from api.v1.chat import router as chat_router

@asynccontextmanager
async def lifecycle_handler(app: FastAPI):
    """
    TideBot 全局组件异步生命周期网关
    可在此处初始化异步底座（如引擎启动、Redis 连接池、数据库迁移检查）
    """
    print(f"[{settings.PROJECT_NAME}] 生产级应用底座初始化启动中...")
    yield
    print(f"[{settings.PROJECT_NAME}] 正在安全释放系统全局核心资源...")

# 初始化 FastAPI 实体驱动
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifecycle_handler
)

# 挂载基础安全跨域插件 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载流式链路追踪高阶中间件
app.add_middleware(TideBotMiddleware)

# 注册统一核心路由分支
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(bot_router, prefix=settings.API_V1_STR)
app.include_router(channel_router, prefix=settings.API_V1_STR)
app.include_router(chat_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    # 支持生产级直接一键拉起 python main.py
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1,
        loop="asyncio"
    )