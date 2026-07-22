from typing import Dict, Any
from adapters.base import BaseAdapter
import logging

logger = logging.getLogger("TideBot")

class TelegramAdapter(BaseAdapter):
    """
    Telegram Bot Webhook 协议解析器
    """
    @property
    def platform_name(self) -> str:
        return "telegram"

    async def parse_and_dispatch(self, raw_payload: Dict[str, Any]) -> bool:
        try:
            message = raw_payload.get("message", {})
            if not message:
                return False

            text = message.get("text")
            if not text:
                logger.info("非文本 TG 消息，当前版本暂忽略。")
                return False

            chat = message.get("chat", {})
            user = message.get("from", {})
            
            session_id = str(chat.get("id", ""))
            user_id = str(user.get("id", ""))
            
            if not session_id or not user_id:
                return False

            await self._publish_message(
                session_id=session_id,
                user_id=user_id,
                content=text,
                metadata={"chat_type": chat.get("type", "private")}
            )
            return True
        except Exception as e:
            logger.error(f"解析 Telegram 消息失败: {e}", exc_info=True)
            return False