from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatMessage(BaseModel):
    """单条聊天消息的校验模型"""
    role: str = Field(..., description="消息发送者角色 (user, assistant, system)")
    content: str = Field(..., description="消息的具体文本内容")

class ChatRequest(BaseModel):
    """用户发起聊天请求的参数模型"""
    session_id: str = Field(..., description="当前会话的唯一标识")
    query: str = Field(..., description="用户当前输入的问题或指令")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="前端传入的最近历史记录，用于补充上下文")
    model_override: Optional[str] = Field(None, description="如果用户指定了特定模型，则覆盖系统默认配置")

class ChatResponse(BaseModel):
    """API 返回给客户端的聊天响应模型"""
    session_id: str
    reply: str = Field(..., description="TideBot 的最终文本回复")
    usage: Optional[Dict[str, int]] = Field(None, description="Token 消耗统计")
    processing_time_ms: Optional[int] = Field(None, description="服务器处理耗时 (毫秒)")