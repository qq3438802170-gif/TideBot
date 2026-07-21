import asyncio
import logging
from typing import Callable, Dict, List, Type, Any
from .events.base import BaseEvent

logger = logging.getLogger("TideBot")

class EventBus:
    """
    系统异步事件总线 (单例模式)
    负责全局事件的发布与订阅注册
    """
    _instance = None
    _subscribers: Dict[Type[BaseEvent], List[Callable]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._subscribers = {}
        return cls._instance

    def subscribe(self, event_type: Type[BaseEvent], handler: Callable):
        """
        订阅特定类型的事件
        :param event_type: 继承自 BaseEvent 的事件类
        :param handler: 异步或同步的回调函数
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"已注册事件订阅: {event_type.__name__} -> {handler.__name__}")

    async def publish(self, event: BaseEvent):
        """
        异步发布事件，通知所有订阅了该事件的处理器
        :param event: 实例化的事件对象
        """
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])
        
        if not handlers:
            logger.debug(f"事件已发布，但无订阅者: {event_type.__name__}")
            return

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"处理事件 {event_type.__name__} 时发生异常: {e}", exc_info=True)