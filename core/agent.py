import logging
import asyncio
import time
from typing import List, Dict, Any, Optional, AsyncGenerator
from core.tokenizer import Tokenizer

logger = logging.getLogger("TideBot.Core.Agent")

class MessageContext:
    """
    Agent 专用的滚动记忆上下文管理对象
    封装了持久化、追加、滑动裁剪等完整语义。
    """
    def __init__(self, session_id: str, max_window_tokens: int = 4096, tokenizer: Tokenizer = None):
        self.session_id: str = session_id
        self.max_window_tokens: int = max_window_tokens
        self.tokenizer: Tokenizer = tokenizer or Tokenizer()
        self.messages: List[Dict[str, Any]] = []
        self.system_prompt: str = "You are TideBot, a professional, secure and intelligent AI assistant platform."

    def set_system_prompt(self, prompt: str) -> None:
        """设置系统级别 Prompt 提示词基底"""
        if prompt:
            self.system_prompt = prompt

    def add_message(self, role: str, content: str, name: Optional[str] = None, tool_calls: Optional[List[Dict[str, Any]]] = None, tool_call_id: Optional[str] = None) -> None:
        """
        向历史上下文中追加结构化数据
        """
        msg: Dict[str, Any] = {"role": role, "content": content}
        if name:
            msg["name"] = name
        if tool_calls:
            msg["tool_calls"] = tool_calls
        if tool_call_id:
            msg["tool_call_id"] = tool_call_id
            
        self.messages.append(msg)

    def compile_history(self, tools_schema: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        实现滑动窗口裁剪。确保总 Token 量不突破大模型输入上限。
        """
        compiled: List[Dict[str, Any]] = [{"role": "system", "content": self.system_prompt}]
        
        if not self.messages:
            return compiled

        # 逆序计算，优先保留最新发生的内容
        allocated_tokens = self.tokenizer.count_chat_tokens(compiled, tools=tools_schema)
        available_tokens = self.max_window_tokens - allocated_tokens
        
        if available_tokens <= 200:
            raise ValueError(f"系统提示词开销过大，剩余可用上下文可用槽位过低：{available_tokens}")

        kept_messages = []
        current_consumed = 0
        
        for msg in reversed(self.messages):
            msg_token = self.tokenizer.count_chat_tokens([msg])
            if current_consumed + msg_token <= available_tokens:
                kept_messages.insert(0, msg)
                current_consumed += msg_token
            else:
                # 触发动态裁剪断点，之后的老记忆被丢弃
                logger.debug(f"上下文滚动窗口满载，历史记忆已触发边缘裁剪，SessionID: {self.session_id}")
                break

        compiled.extend(kept_messages)
        return compiled

    def clear(self) -> None:
        """清空该会话下的所有历史短期记忆"""
        self.messages.clear()


class AgentRuntime:
    """
    核心 Agent 运行时处理器
    驱动状态循环，拼装全链路 Prompt 并无缝执行 LLM 通信。
    """
    def __init__(self, agent_id: str, tokenizer: Tokenizer, default_max_tokens: int = 8192):
        self.agent_id: str = agent_id
        self.tokenizer: Tokenizer = tokenizer
        self.default_max_tokens: int = default_max_tokens
        self._sessions: Dict[str, MessageContext] = {}
        self.available_tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, name: str, schema: Dict[str, Any], handler: Any) -> None:
        """
        注册 Agent 可直接调用的外部原子工具能力
        """
        self.available_tools[name] = {
            "schema": schema,
            "handler": handler
        }
        logger.debug(f"Agent [{self.agent_id}] 成功绑定功能工具: {name}")

    def get_context(self, session_id: str) -> MessageContext:
        """获取或创建对应的会话记忆上下文"""
        if session_id not in self._sessions:
            self._sessions[session_id] = MessageContext(session_id, self.default_max_tokens, self.tokenizer)
        return self._sessions[session_id]

    async def execute_thought_loop(self, session_id: str, user_input: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        核心思考循环：支持动态工具调用（Function Calling）、多轮自治迭代、流式实时响应
        """
        context = self.get_context(session_id)
        context.add_message(role="user", content=user_input)
        
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            tools_schema = [t["schema"] for t in self.available_tools.values()] if self.available_tools else None
            prompt_messages = context.compile_history(tools_schema=tools_schema)
            
            logger.debug(f"提交至 Agent LLM 引擎的消息流层级数: {len(prompt_messages)}")
            
            # 此处应对接底层大模型基础设施。以下给出具备完全完整生产逻辑的代码框架。
            # 为了维持高可用无状态架构，采用模拟的底层驱动引擎。
            response_content = ""
            tool_calls_to_exec = []
            
            # 模拟模型推理与思考流输出（生产环境将替换为正式的底层 LLM 客户端驱动）
            await asyncio.sleep(0.1) 
            
            # 特殊指令词匹配，用于模拟拦截机制与功能测试演示
            if "呼叫工具" in user_input and iteration == 1:
                tool_name = "get_weather"
                if tool_name in self.available_tools:
                    tool_calls_to_exec = [{
                        "id": f"call_{int(time.time())}",
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": '{"location": "Goyang-si"}'
                        }
                    }]
            else:
                response_content = f"【模型响应】已收到会话需求。针对您的输入：“{user_input}”，TideBot 核心运行时运转正常。"
            
            if tool_calls_to_exec:
                # 记录大模型决定调用工具的动作
                context.add_message(role="assistant", content="", tool_calls=tool_calls_to_exec)
                yield {"type": "status", "content": f"Agent 决策：触发工具链自动化执行：{[t['function']['name'] for t in tool_calls_to_exec]}..."}
                
                for tool_call in tool_calls_to_exec:
                    f_name = tool_call["function"]["name"]
                    f_args = tool_call["function"]["arguments"]
                    call_id = tool_call["id"]
                    
                    handler = self.available_tools[f_name]["handler"]
                    try:
                        # 动态异步触发工具动作
                        tool_result = await handler(f_args)
                        context.add_message(role="tool", content=str(tool_result), name=f_name, tool_call_id=call_id)
                        yield {"type": "tool_result", "tool_name": f_name, "result": tool_result}
                    except Exception as exc:
                        logger.error(f"工具执行层灾难性阻断：{f_name}，详情: {str(exc)}")
                        context.add_message(role="tool", content=f"Error executing tool: {str(exc)}", name=f_name, tool_call_id=call_id)
                
                # 工具执行完毕，继续进入当前 thought_loop 的下一轮自回归推理
                continue
            else:
                # 无工具调用，证明思考闭环，追加最终助手回复并打破循环
                context.add_message(role="assistant", content=response_content)
                yield {"type": "text", "content": response_content}
                break