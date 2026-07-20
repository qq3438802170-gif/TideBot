import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

# 假设我们在 core/config 中管理配置 (后续实现)
# from tidebot.core.config import settings

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    TideBot 全局生命周期管理
    在此处初始化数据库连接池、加载内置工具、扫描并挂载用户插件。
    """
    logger.info("TideBot is starting up...")
    
    # 1. 初始化数据库连接
    # await db_manager.connect()
    
    # 2. 注册内置底层工具 (例如：WebSearchTool)
    # tool_registry.register(WebSearchTool())
    
    # 3. 动态加载用户插件
    # plugin_manager.load_all_plugins(settings.PLUGINS_DIR)
    
    yield
    
    logger.info("TideBot is shutting down...")
    # 清理资源、关闭连接等
    # await db_manager.disconnect()

def create_app() -> FastAPI:
    """
    工厂模式创建 FastAPI 应用实例，便于测试和后续扩展。
    """
    app = FastAPI(
        title="TideBot API",
        description="Core API for the TideBot modern AI Agent platform.",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        default_response_class=ORJSONResponse, # 提升序列化性能
        lifespan=lifespan,
    )

    # 跨域配置 - 针对 Web Dashboard 和 Mobile App 通信
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应通过 settings.BACKEND_CORS_ORIGINS 严格限制
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由 (后续建立 api 模块后取消注释)
    # from tidebot.api.v1.router import api_router
    # app.include_router(api_router, prefix="/api/v1")

    @app.get("/health", tags=["System"])
    async def health_check() -> dict[str, str]:
        """系统健康检查接口"""
        return {"status": "ok", "service": "TideBot Core"}

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    # 仅用于本地直接运行 python main.py，标准运行方式推荐使用 CLI
    uvicorn.run("tidebot.main:app", host="0.0.0.0", port=8000, reload=True)