from typing import Optional, Dict, Any
from .base import BaseEvent

class MessageReceivedEvent(BaseEvent):
    """用户或外部系统发送消息到达 TideBot 时的事件"""
    session_id: str
    user_id: str
    platform: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class MessageReplyEvent(BaseEvent):
    """TideBot 处理完毕，准备向外部系统发送回复时的事件"""
    session_id: str
    receiver_id: str
    platform: str
    reply_content: str
    metadata: Optional[Dict[str, Any]] = None