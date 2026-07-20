import pydantic
from typing import List, Dict, Any, Optional, AsyncGenerator
from abc import ABC, abstractmethod

class MultimodalContent(pydantic.BaseModel):
    """
    高质感多模态输入元素契约
    """
    type: str # "text" | "image_url" | "audio_url"
    text: Optional[str] = None
    image_url: Optional[Dict[str, str]] = None # {"url": "..."}

class ChatMessage(pydantic.BaseModel):
    """
    TideBot 全局统一网关规范消息体
    """
    role: str # "system" | "user" | "assistant" | "tool"
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class BaseGateway(ABC):
    """
    LLM 统一抽象网关基类 (符合 DIP 依赖倒置原则)
    """
    def __init__(self, model_name: str, api_key: str, base_url: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    async def generate(self, messages: List[ChatMessage], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        标准原子一元响应调用契约
        """
        pass

    @abstractmethod
    async def generate_stream(self, messages: List[ChatMessage], tools: Optional[List[Dict[str, Any]]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """
        高性能工业级全双工流式相应返回契约
        """
        pass