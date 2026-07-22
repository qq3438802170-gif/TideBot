import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(log_level: int = logging.INFO) -> logging.Logger:
    """
    配置并初始化全局日志系统
    支持控制台输出与基于文件大小自动轮转的持久化文件输出
    """
    logger = logging.getLogger("TideBot")
    logger.setLevel(log_level)

    # 避免重复添加 Handler 导致日志重复打印
    if logger.handlers:
        return logger

    # 定义统一的日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. 控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. 文件轮转日志处理器 (单文件最大 10MB，保留最近 5 个备份)
    log_dir = os.path.join("data", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "tidebot_system.log")

    file_handler = RotatingFileHandler(
        filename=log_file_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("系统日志模块初始化完成。")
    return logger