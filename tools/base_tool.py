from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """
    系统工具的抽象基类
    所有的 Agent 工具都应该继承此类并实现其方法，以便统一注册
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """工具的全局唯一名称，仅限英文和下划线"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """工具的详细描述，大模型将根据此描述决定是否调用"""
        pass

    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """
        返回工具所需参数的 JSON Schema 定义
        """
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """
        工具的实际执行逻辑
        返回值必须是字符串形式，以便大模型理解
        """
        pass