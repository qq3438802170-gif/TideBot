import logging
from typing import Callable, Dict, Any

logger = logging.getLogger("TideBot")

class CapabilityRegistry:
    """全局能力中心 (单例)，负责注册和发现所有的工具和插件"""
    
    _instance = None
    _tools: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CapabilityRegistry, cls).__new__(cls)
            cls._instance._tools = {}
        return cls._instance

    def register_tool(self, name: str, description: str, func: Callable, parameters: Dict[str, Any]):
        """
        注册一个可以在大模型 Function Calling 中使用的工具
        :param parameters: 遵循 JSON Schema 规范的参数定义
        """
        if name in self._tools:
            logger.warning(f"工具 [{name}] 已存在，将被覆盖。")
            
        self._tools[name] = {
            "name": name,
            "description": description,
            "func": func,
            "parameters": parameters
        }
        logger.debug(f"已成功注册工具: {name}")

    def get_tool(self, name: str) -> Callable:
        """获取指定名称的工具执行函数"""
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"未找到名为 {name} 的工具")
        return tool["func"]

    def get_all_tools_schema(self) -> list:
        """获取所有已注册工具的 JSON Schema，用于传递给 LLM"""
        schemas = []
        for name, meta in self._tools.items():
            schemas.append({
                "type": "function",
                "function": {
                    "name": meta["name"],
                    "description": meta["description"],
                    "parameters": meta["parameters"]
                }
            })
        return schemas