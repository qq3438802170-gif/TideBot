from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
from core.event_bus import EventBus
from core.events.message import MessageReceivedEvent

logger = logging.getLogger("TideBot")

class BaseAdapter(ABC):
    """
    IM 接入层基类
    所有社交平台的适配器都必须继承此类
    """
    def __init__(self):
        self.event_bus = EventBus()

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """返回平台唯一标识，例如：wechat, telegram, qq"""
        pass

    @abstractmethod
    async def parse_and_dispatch(self, raw_payload: Dict[str, Any]) -> bool:
        """
        解析原始 Webhook 载荷，如果有效，则派发到 EventBus
        :return: 解析是否成功
        """
        pass

    async def _publish_message(self, session_id: str, user_id: str, content: str, metadata: Dict[str, Any] = None):
        """通用方法：将解析好的数据转换为系统事件并发布"""
        event = MessageReceivedEvent(
            session_id=session_id,
            user_id=user_id,
            platform=self.platform_name,
            content=content,
            metadata=metadata or {}
        )
        await self.event_bus.publish(event)
        logger.debug(f"[{self.platform_name}] 已成功解析并派发消息: {content[:20]}...")