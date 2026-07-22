from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator

class BaseLLMProvider(ABC):
    """
    所有大模型接入的抽象基类
    要求子类必须实现非流式和流式两个接口
    """
    
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        非流式生成接口
        :param messages: OpenAI 格式的上下文列表
        :return: 包含内容和元数据(如token消耗)的字典
        """
        pass

    @abstractmethod
    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """
        流式生成接口
        :param messages: OpenAI 格式的上下文列表
        :yield: 逐步生成的文本片段
        """
        pass