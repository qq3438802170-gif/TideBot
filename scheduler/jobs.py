import logging
from datetime import datetime, timezone
from core.database.connection import AsyncSessionLocal
# 假设有相应的仓储操作
# from core.database.repository import ChatHistoryRepository 

logger = logging.getLogger("TideBot")

async def cleanup_expired_memory_job():
    """
    后台任务示例：清理过期的聊天历史记录
    此任务可以由 TaskManager 安排在每天凌晨执行
    """
    logger.info("开始执行定时任务：清理过期会话记忆...")
    try:
        # 这里是数据库操作的示范
        async with AsyncSessionLocal() as session:
            # 实际业务中，可以调用 Repository 封装的方法删除 30 天前的数据
            # repo = ChatHistoryRepository(session)
            # await repo.delete_old_history(days=30)
            pass
        logger.info("定时任务执行完毕：清理过期会话记忆成功。")
    except Exception as e:
        logger.error(f"清理过期会话记忆任务失败: {e}", exc_info=True)

def register_all_jobs(task_manager):
    """
    集中注册所有系统预设的定时任务
    """
    # 每天凌晨 3:00 执行清理任务
    task_manager.add_cron_job(
        func=cleanup_expired_memory_job,
        cron_expr="0 3 * * *",
        job_id="daily_memory_cleanup"
    )