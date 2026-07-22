import logging
import json
from typing import AsyncGenerator
from core.llm.router import LLMRouter
from core.capabilities.registry import CapabilityRegistry
from core.agent.context import AgentContext
from core.agent.persona import PersonaBuilder
from core.memory.sliding_window import SlidingWindowMemory
from core.event_bus import EventBus
from core.events.agent import AgentExecutionStartedEvent, AgentExecutionFinishedEvent

logger = logging.getLogger("TideBot")

class AgentExecutor:
    """
    Agent 核心执行引擎
    负责统筹记忆、能力、规划器，并协调大模型执行 ReAct 或 Function Calling 循环
    """
    
    def __init__(self):
        self.llm_router = LLMRouter()
        self.registry = CapabilityRegistry()
        self.memory = SlidingWindowMemory()
        self.event_bus = EventBus()

    async def execute(self, context: AgentContext) -> str:
        """
        执行一次完整的 Agent 思考逻辑（非流式）
        包含组装上下文、发起 LLM 请求、拦截工具调用并执行回调
        """
        # 发布开始事件
        await self.event_bus.publish(AgentExecutionStartedEvent(
            session_id=context.session_id,
            task_intent=context.original_query
        ))

        system_msg = PersonaBuilder.build_system_prompt()
        # 利用滑动窗口截断历史记忆
        prepared_messages = self.memory.truncate(system_msg, context.messages)
        tools = self.registry.get_all_tools_schema()

        max_iterations = 5  # 防止工具调用死循环
        iteration = 0

        while not context.is_finished and iteration < max_iterations:
            iteration += 1
            
            # 由于部分 LLM 接口差异，这里伪代码展示包含 tools 的 kwargs 参数传递
            kwargs = {}
            if tools:
                kwargs["tools"] = tools

            # 1. 询问大模型
            response = await self.llm_router.generate(prepared_messages, **kwargs)
            content = response.get("content")
            
            # 2. 解析大模型回复，判断是否触发了工具调用 (此处假设 response 包含 tool_calls 结构，实际需根据官方 SDK 数据结构适配)
            # 在生产环境中，你需要解析 OpenAI 返回的 message.tool_calls
            tool_calls = response.get("tool_calls", [])

            if not tool_calls:
                # 模型直接给出了最终答案
                context.is_finished = True
                context.final_answer = content or "（模型返回为空）"
                break
                
            # 3. 循环执行工具调用
            prepared_messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls})
            
            for tool_call in tool_calls:
                func_name = tool_call["function"]["name"]
                try:
                    args = json.loads(tool_call["function"]["arguments"])
                    logger.info(f"Agent 决定调用工具: {func_name}, 参数: {args}")
                    
                    tool_func = self.registry.get_tool(func_name)
                    # 如果工具是异步的，需要 await；这里为了演示使用同步调用
                    result = tool_func(**args) 
                    
                    # 将工具结果追加进上下文中供下一轮循环读取
                    prepared_messages.append({
                        "role": "tool", 
                        "tool_call_id": tool_call["id"],
                        "name": func_name,
                        "content": str(result)
                    })
                except Exception as e:
                    logger.error(f"工具 {func_name} 执行异常: {e}")
                    prepared_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": func_name,
                        "content": f"Error: {str(e)}"
                    })

        # 如果超出了循环次数，强制结束
        if not context.is_finished:
            context.final_answer = "抱歉，任务执行过程过于复杂，已自动中止。"

        # 发布结束事件
        await self.event_bus.publish(AgentExecutionFinishedEvent(
            session_id=context.session_id,
            final_result=context.final_answer,
            success=True
        ))

        return context.final_answer