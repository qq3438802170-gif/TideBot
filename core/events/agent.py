from typing import Dict, Any, Optional
from .base import BaseEvent

class AgentExecutionStartedEvent(BaseEvent):
    """Agent 开始接管并规划任务的事件"""
    session_id: str
    task_intent: str

class ToolCallEvent(BaseEvent):
    """Agent 决定调用外部系统工具 (Function Calling) 的事件"""
    session_id: str
    tool_name: str
    tool_arguments: Dict[str, Any]

class AgentExecutionFinishedEvent(BaseEvent):
    """Agent 完成任务执行周期的事件"""
    session_id: str
    final_result: str
    success: bool
    error_message: Optional[str] = None