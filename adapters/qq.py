from typing import Dict, Any
from adapters.base import BaseAdapter
import logging

logger = logging.getLogger("TideBot")

class QQAdapter(BaseAdapter):
    """
    基于 OneBot (原 CQHttp) v11 标准的 QQ 消息解析器
    """
    @property
    def platform_name(self) -> str:
        return "qq"

    async def parse_and_dispatch(self, raw_payload: Dict[str, Any]) -> bool:
        try:
            post_type = raw_payload.get("post_type")
            if post_type != "message":
                return False

            msg_type = raw_payload.get("message_type")
            user_id = str(raw_payload.get("user_id", ""))
            content = raw_payload.get("raw_message", "")
            
            session_id = user_id
            if msg_type == "group":
                group_id = str(raw_payload.get("group_id", ""))
                session_id = f"group_{group_id}"
                
            await self._publish_message(
                session_id=session_id,
                user_id=user_id,
                content=content,
                metadata={"msg_type": msg_type}
            )
            return True
        except Exception as e:
            logger.error(f"解析 QQ(OneBot) 消息失败: {e}", exc_info=True)
            return False