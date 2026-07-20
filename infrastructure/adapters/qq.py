import logging
import asyncio
import json
import aiohttp
from typing import Dict, Any, Optional
from core.event_bus import EventBus, Event

logger = logging.getLogger("TideBot.Infrastructure.Adapter.QQ")

class QQAdapter:
    """
    QQ OneBot v11 / Lagrange 异步协议长连接驱动适配器
    基于高性能 WebSockets 双工通信模式，提供全面可靠的消息收发转换。
    """
    def __init__(self, event_bus: EventBus, config: Dict[str, Any]):
        self.event_bus: EventBus = event_bus
        self.ws_url: str = config.get("ws_url", "ws://127.0.0.1:8080")
        self.access_token: str = config.get("access_token", "")
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._is_running: bool = False
        self._loop_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """建立 WebSocket 长连接双工通信"""
        self._session = aiohttp.ClientSession()
        self._is_running = True
        
        self.event_bus.subscribe("agent.loop.respond", self._handle_outbound_reply)
        self._loop_task = asyncio.create_task(self._connection_watcher())
        logger.info(f"QQ OneBot 协议适配层挂载完成，目标中继端: {self.ws_url}")

    async def _connection_watcher(self) -> None:
        """断线自动重连看门狗"""
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
        while self._is_running:
            try:
                async with self._session.ws_connect(self.ws_url, headers=headers) as ws:
                    self._ws = ws
                    logger.info("与 OneBot 服务端握手建立完毕，进入全双工监听收发态。")
                    
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            payload = json.loads(msg.data)
                            await self._process_onebot_frame(payload)
                        elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                            break
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"OneBot 通道连线断开或拒绝访问: {str(e)}，将在 5 秒后执行重连...")
                await asyncio.sleep(5)

    async def _process_onebot_frame(self, frame: Dict[str, Any]) -> None:
        """
        清洗 OneBot 事件元数据
        """
        # 仅截获核心消息类型事件，过滤心跳等无状态信令
        if frame.get("post_type") != "message":
            return

        msg_type = frame.get("message_type") # private / group
        sender_id = str(frame.get("user_id"))
        
        session_id = f"qq_private_{sender_id}" if msg_type == "private" else f"qq_group_{frame.get('group_id')}"
        raw_msg = frame.get("message", "")
        
        # 标准化文本转换逻辑 (剔除 CQ 码带来的噪声)
        text_content = ""
        if isinstance(raw_msg, str):
            text_content = raw_msg
        elif isinstance(raw_msg, list): # 结构化卡片消息流
            text_content = "".join([m.get("data", {}).get("text", "") for m in raw_msg if m.get("type") == "text"])

        normalized = {
            "platform": "qq",
            "sender_id": sender_id,
            "session_id": session_id,
            "text": text_content.strip(),
            "target_agent_id": "default_agent"
        }
        
        await self.event_bus.publish(Event(name="im.message.received", data=normalized))

    async def _handle_outbound_reply(self, event: Event) -> None:
        """底层回复下发分发逻辑"""
        data = event.data
        if data.get("platform") != "qq" or not self._ws:
            return

        session_str = data.get("session_id", "")
        
        # 结构解构恢复：解析私聊或是群组下发
        action = "send_private_msg" if "private" in session_str else "send_group_msg"
        target_field = "user_id" if "private" in session_str else "group_id"
        target_id = int(session_str.split("_")[-1])

        ws_frame = {
            "action": action,
            "params": {
                target_field: target_id,
                "message": data.get("reply_text")
            }
        }
        try:
            await self._ws.send_json(ws_frame)
            logger.debug(f"QQ 异步物理响应帧已成功投递发送。")
        except Exception as e:
            logger.error(f"QQ 物理帧下发流遭遇崩溃损坏: {str(e)}")

    async def stop(self) -> None:
        """关闭通道连接"""
        self._is_running = False
        if self._loop_task:
            self._loop_task.cancel()
        if self._session:
            await self._session.close()
        logger.info("QQ OneBot 适配驱动模块已完全注销下线。")