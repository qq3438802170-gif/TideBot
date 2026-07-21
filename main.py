import asyncio
import sys
import logging

# 假设核心引导程序存在于 core/bootstrap.py 中
from core.bootstrap import main as bootstrap_main

def start():
    """TideBot 启动入口函数"""
    print("🌊 正在启动 TideBot AI Agent 核心引擎...")
    try:
        # 运行核心层定义好的异步引导生命周期
        asyncio.run(bootstrap_main())
    except KeyboardInterrupt:
        print("\n[TideBot] 收到退出信号 (Ctrl+C)，正在安全关闭服务...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"[TideBot] 启动失败，发生致命错误: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    start()