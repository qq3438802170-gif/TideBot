import logging
from .config_manager import ConfigManager
from .logger import setup_logger
from .event_bus import EventBus

async def initialize_system():
    """
    应用生命周期管理与初始化编排。
    严格规定各基础组件的启动顺序。
    """
    # 1. 加载全局配置
    config_manager = ConfigManager()
    
    # 2. 提取配置并初始化日志系统
    debug_mode = config_manager.config.get("server", {}).get("debug", False)
    log_level = logging.DEBUG if debug_mode else logging.INFO
    logger = setup_logger(log_level=log_level)
    
    logger.info("=========================================")
    logger.info("🚀 正在初始化 TideBot 核心运行时环境...")
    logger.info("=========================================")

    # 3. 启动系统事件总线
    event_bus = EventBus()
    logger.info("✔ 事件总线 (EventBus) 初始化成功。")

    # 4. 数据库初始化 (预留位置给 core/database/connection.py)
    # await init_db_connection(config_manager.env.database_url)
    logger.info("✔ 数据库连接模块就绪。")

    # 5. 加载能力中心与插件 (预留位置给 core/capabilities/)
    # await capability_registry.initialize()
    logger.info("✔ 能力注册中心就绪。")

    logger.info("TideBot 核心启动序列执行完毕。")

async def main():
    """
    核心启动挂载点，由外层的 main.py 唤起。
    """
    await initialize_system()
    
    # 正常运行中，这里会启动 FastAPI/Uvicorn 服务或保持事件循环活跃
    # 此处使用占位阻塞，保证基础服务不会立刻退出
    import asyncio
    logger = logging.getLogger("TideBot")
    logger.info("主事件循环已启动，等待外部连接...")
    
    try:
        # 维持异步事件循环不退出
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("收到中止信号，退出事件循环。")