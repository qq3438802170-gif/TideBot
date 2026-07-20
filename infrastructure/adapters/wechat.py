import logging
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from core.event_bus import EventBus, Event

logger = logging.getLogger("TideBot.Infrastructure.Adapter.WeChat")

class WeChatAdapter:
    """
    微信 OpenClaw 协议与 ClawBot 高级适配适配层
    支持双向长轮询监听/Webhook 机制，将异构微信消息转化为标准统一事件发布至核心 EventBus。
    """
    def __init__(self, event_bus: EventBus, config: Dict[str, Any]):
        self.event_bus: EventBus = event_bus
        self.api_url: str = config.get("api_url", "http://127.0.0.1:8055")
        self.secret_token: str = config.get("secret_token", "")
        self._session: Optional[aiohttp.ClientSession] = None
        self._is_running: bool = False
        self._listen_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """启动适配器收发流水线监听"""
        self._session = aiohttp.ClientSession(headers={
            "Authorization": f"Bearer {self.secret_token}" if self.secret_token else ""
        })
        self._is_running = True
        
        # 挂载核心出站回执事件监听（实现无缝解耦发送响应）
        self.event_bus.subscribe("agent.loop.respond", self._handle_outbound_reply)
        
        # 启动异步长轮询守候微协程
        self._listen_task = asyncio.create_task(self._message_listener_loop())
        logger.info("微信 OpenClaw 协议通道适配器成功挂载启动。")

    async def _message_listener_loop(self) -> None:
        """长轮询网关服务监听"""
        while self._is_running:
            try:
                # 模拟轮询或接收 OpenClaw API 推送流
                async with self._session.get(f"{self.api_url}/queue/receive", timeout=30) as resp:
                    if resp.status == 200:
                        payload = await resp.json()
                        await self._process_raw_wechat_msg(payload)
                    elif resp.status == 204: # 无消息进入挂起
                        await asyncio.sleep(0.5)
                    else:
                        await asyncio.sleep(5) # 容错挂起
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"微信底层协议监听流发生异常扰断: {str(e)}")
                await asyncio.sleep(5)

    async def _process_raw_wechat_msg(self, raw: Dict[str, Any]) -> None:
        """
        数据清洗：将 OpenClaw 微信私有数据转换为 TideBot 标准泛化格式
        """
        # 判断是否为群组消息
        is_group = "@chatroom" in raw.get("from_user", "")
        
        normalized_payload = {
            "platform": "wechat",
            "sender_id": raw.get("from_user"),
            "session_id": raw.get("from_user") if not is_group else raw.get("chatroom_id"),
            "text": raw.get("content", "").strip(),
            "target_agent_id": "default_agent",
            "raw_meta": raw
        }
        
        # 构建统一入站事件推向总线
        ingress_event = Event(name="im.message.received", data=normalized_payload)
        await self.event_bus.publish(ingress_event)

    async def _handle_outbound_reply(self, event: Event) -> None:
        """
        消费发送回执事件，执行物理发送
        """
        data = event.data
        if data.get("platform") != "wechat":
            return # 忽略非本平台的下行流量

        payload = {
            "to_user": data.get("session_id"),
            "msg_type": "text",
            "content": data.get("reply_text")
        }
        
        try:
            async with self._session.post(f"{self.api_url}/message/send", json=payload) as resp:
                if resp.status == 200:
                    logger.debug(f"微信回执消息包成功通过 OpenClaw 离岸物理下发。")
                else:
                    logger.error(f"微信回执发送未达预期，HTTP 状态码: {resp.status}")
        except Exception as e:
            logger.error(f"微信物理链路发送崩溃，详情: {str(e)}")

    async def stop(self) -> None:
        """安全释放适配器句柄"""
        self._is_running = False
        if self._listen_task:
            self._listen_task.cancel()
        if self._session:
            await self._session.close()
        logger.info("微信适配器已优雅停止卸载。")