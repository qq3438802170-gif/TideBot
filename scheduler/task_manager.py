import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("TideBot")

class TaskManager:
    """
    全局后台定时任务管理器 (单例)
    基于 APScheduler，支持异步任务
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskManager, cls).__new__(cls)
            cls._instance.scheduler = AsyncIOScheduler()
            cls._instance._is_running = False
        return cls._instance

    def start(self):
        """启动调度器"""
        if not self._is_running:
            self.scheduler.start()
            self._is_running = True
            logger.info("后台定时任务调度器 (TaskManager) 已启动。")

    def shutdown(self):
        """安全关闭调度器"""
        if self._is_running:
            self.scheduler.shutdown()
            self._is_running = False
            logger.info("后台定时任务调度器已安全关闭。")

    def add_cron_job(self, func, cron_expr: str, job_id: str):
        """
        添加一个基于 Cron 表达式的定时任务
        :param func: 要执行的异步或同步函数
        :param cron_expr: 类似 '0 0 * * *' 的 Cron 表达式
        :param job_id: 任务唯一标识
        """
        trigger = CronTrigger.from_crontab(cron_expr)
        self.scheduler.add_job(func, trigger=trigger, id=job_id, replace_existing=True)
        logger.debug(f"已注册定时任务: {job_id}, 触发规则: {cron_expr}")