from typing import Dict, Any
from adapters.base import BaseAdapter
import logging

logger = logging.getLogger("TideBot")

class WeChatAdapter(BaseAdapter):
    """
    微信公众号 / 个人号 (基于 Wechaty 等) 协议解析器
    """
    @property
    def platform_name(self) -> str:
        return "wechat"

    async def parse_and_dispatch(self, raw_payload: Dict[str, Any]) -> bool:
        try:
            # 此处以类似 Wechaty 的 JSON 结构为例
            # 实际结构取决于你最终使用的微信接入方案 (如个微 Hooker 或 企微 API)
            msg_type = raw_payload.get("type")
            if msg_type != "text":
                logger.info("非文本微信消息，当前版本暂忽略。")
                return False

            content = raw_payload.get("text", "")
            user_id = raw_payload.get("talkerId", "unknown_wx_user")
            room_id = raw_payload.get("roomId") # 如果在群聊中
            
            # 会话 ID 策略：如果是群聊则用群 ID，私聊则用用户 ID
            session_id = room_id if room_id else user_id

            await self._publish_message(
                session_id=session_id,
                user_id=user_id,
                content=content,
                metadata={"is_room": bool(room_id)}
            )
            return True
        except Exception as e:
            logger.error(f"解析微信消息失败: {e}", exc_info=True)
            return False