import logging
import uuid
import time
from typing import Dict, Any, Callable, Awaitable
from core.event_bus import EventBus, Event, EventPriority
from core.tokenizer import Tokenizer
from core.agent import AgentRuntime

logger = logging.getLogger("TideBot.Core.MessageEngine")

class MessageEngine:
    """
    TideBot 消息调度与控制中枢
    接收外部 IM 平台的输入，转化为标准化流水线，管理跨模块的中间拦截和响应分发。
    """
    def __init__(self, event_bus: EventBus, tokenizer: Tokenizer):
        self.event_bus: EventBus = event_bus
        self.tokenizer: Tokenizer = tokenizer
        self.active_runtimes: Dict[str, AgentRuntime] = {}
        self._init_base_pipelines()

    def _init_base_pipelines(self) -> None:
        """
        内置注册核心总线调度机制，解耦处理拓扑
        """
        self.event_bus.subscribe("im.message.received", self._pipeline_ingress, EventPriority.NORMAL)
        self.event_bus.subscribe("agent.loop.respond", self._pipeline_egress, EventPriority.NORMAL)

    def attach_agent_runtime(self, runtime: AgentRuntime) -> None:
        """将就绪的 Agent 运行时实例锚定到调度器中"""
        if runtime.agent_id not in self.active_runtimes:
            self.active_runtimes[runtime.agent_id] = runtime
            logger.info(f"调度系统已成功挂载 Agent 实例集群锚点: [{runtime.agent_id}]")

    async def handle_im_message(self, raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        外部网关/网络适配器调用的主入口。
        将异构数据结构化，推入总线管线。
        """
        trace_id = str(uuid.uuid4())
        logger.debug(f"监听到入站流量，分配系统内部 TraceID: {trace_id}")
        
        # 将原始负载包装为 TideBot 标准事件规范
        normalized_data = {
            "trace_id": trace_id,
            "platform": raw_payload.get("platform", "generic"),
            "sender_id": raw_payload.get("sender_id", "anonymous"),
            "session_id": raw_payload.get("session_id", f"sess_{int(time.time())}"),
            "message_text": raw_payload.get("text", ""),
            "agent_id": raw_payload.get("target_agent_id", "default_agent"),
            "timestamp": time.time()
        }
        
        ingress_event = Event(name="im.message.received", data=normalized_data)
        
        # 发布到事件总线，触发各级别插件的过滤、预处理与核心匹配
        await self.event_bus.publish(ingress_event)
        
        if ingress_event.is_cancelled:
            return {
                "status": "rejected",
                "trace_id": trace_id,
                "reason": ingress_event.data.get("reject_reason", "被拦截器阻断")
            }
            
        return {
            "status": "processed",
            "trace_id": trace_id,
            "result": ingress_event.result
        }

    async def _pipeline_ingress(self, event: Event) -> None:
        """
        核心输入总线管道实现：匹配 Agent 运行时并触发多轮循环
        """
        data = event.data
        agent_id = data.get("agent_id")
        session_id = data.get("session_id")
        text_content = data.get("message_text")

        runtime = self.active_runtimes.get(agent_id)
        if not runtime:
            # 动态降级路由
            if self.active_runtimes:
                fallback_id = list(self.active_runtimes.keys())[0]
                runtime = self.active_runtimes[fallback_id]
                logger.warning(f"由于未找到指定 Agent [{agent_id}]，系统已自动降级至备用 Agent: {fallback_id}")
            else:
                event.stop_propagation()
                event.set_result("No active agent runtimes registered inside TideBot core ecosystem.")
                return

        final_responses = []
        
        # 执行 Agent 深度推理 Thought 状态自闭环
        async for chunk in runtime.execute_thought_loop(session_id, text_content):
            # 将每次迭代产生的结果向外广播（例如提供给 Web 平台做流式渲染或状态捕获）
            chunk_event = Event(name="agent.loop.step", data={
                "trace_id": data.get("trace_id"),
                "session_id": session_id,
                "chunk": chunk
            })
            await self.event_bus.publish(chunk_event)
            
            if chunk["type"] == "text":
                final_responses.append(chunk["content"])

        combined_text = "\n".join(final_responses)
        event.set_result(combined_text)

        # 触发后置响应总线管道
        egress_event = Event(name="agent.loop.respond", data={
            "trace_id": data.get("trace_id"),
            "session_id": session_id,
            "platform": data.get("platform"),
            "sender_id": data.get("sender_id"),
            "reply_text": combined_text
        })
        await self.event_bus.publish(egress_event)

    async def _pipeline_egress(self, event: Event) -> None:
        """
        后置响应发送管道逻辑
        可在此处对接外发网络请求回执或进行合规性审计过滤。
        """
        logger.debug(f"TraceID: {event.data.get('trace_id')} 的核心响应流已成功离岸。")