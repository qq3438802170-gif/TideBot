import logging
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from core.event_bus import EventBus, Event

logger = logging.getLogger("TideBot.Infrastructure.Adapter.Telegram")

class TelegramAdapter:
    """
    Telegram Bot API 原生高性能异步轮询驱动器
    通过 GetUpdates 滚动消费模型设计，确保海外/分布式基础设施下的高弹性数据流动。
    """
    def __init__(self, event_bus: EventBus, config: Dict[str, Any]):
        self.event_bus: EventBus = event_bus
        self.token: str = config.get("token", "")
        self.api_base: str = f"https://api.telegram.org/bot{self.token}"
        self.proxy: Optional[str] = config.get("proxy", None)
        self._session: Optional[aiohttp.ClientSession] = None
        self._is_running: bool = False
        self._offset: int = 0
        self._poll_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        if not self.token:
            logger.error("Telegram 驱动初始化失败：未提供合法的 Token 凭证。")
            return
            
        self._session = aiohttp.ClientSession()
        self._is_running = True
        
        self.event_bus.subscribe("agent.loop.respond", self._handle_outbound_reply)
        self._poll_task = asyncio.create_task(self._polling_loop())
        logger.info("Telegram Bot 异步适配器已完全就绪并进入接收态。")

    async def _polling_loop(self) -> None:
        """高鲁棒性滚动 Offset 滚动消费流"""
        while self._is_running:
            try:
                url = f"{self.api_base}/getUpdates?offset={self._offset}&timeout=20"
                async with self._session.get(url, proxy=self.proxy, timeout=25) as resp:
                    if resp.status != 200:
                        await asyncio.sleep(5)
                        continue
                    
                    payload = await resp.json()
                    if not payload.get("ok"):
                        continue
                        
                    for update in payload.get("result", []):
                        self._offset = update["update_id"] + 1
                        if "message" in update:
                            await self._process_tg_message(update["message"])
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Telegram 轮询边缘突发致命通信中断: {str(e)}")
                await asyncio.sleep(5)

    async def _process_tg_message(self, message: Dict[str, Any]) -> None:
        """清洗转换 Telegram 异构载荷"""
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        sender_id = message.get("from", {}).get("id")
        
        if not text:
            return # 暂时无视纯媒体流或非文字载荷
            
        normalized = {
            "platform": "telegram",
            "sender_id": str(sender_id),
            "session_id": str(chat_id),
            "text": text,
            "target_agent_id": "default_agent"
        }
        await self.event_bus.publish(Event(name="im.message.received", data=normalized))

    async def _handle_outbound_reply(self, event: Event) -> None:
        data = event.data
        if data.get("platform") != "telegram":
            return

        url = f"{self.api_base}/sendMessage"
        payload = {
            "chat_id": data.get("session_id"),
            "text": data.get("reply_text"),
            "parse_mode": "Markdown" # 开启标准 UI/UX 高级感渲染支持
        }
        try:
            async with self._session.post(url, json=payload, proxy=self.proxy) as resp:
                if resp.status != 200:
                    logger.error(f"Telegram 发送失败异常，底层 HTTP Code: {resp.status}")
        except Exception as e:
            logger.error(f"Telegram 下行物理下发灾难性失效: {str(e)}")

    async def stop(self) -> None:
        self._is_running = False
        if self._poll_task:
            self._poll_task.cancel()
        if self._session:
            await self._session.close()
        logger.info("Telegram 接入侧组件已优雅析构。")