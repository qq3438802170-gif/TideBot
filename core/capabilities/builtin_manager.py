from datetime import datetime, timezone
from .registry import CapabilityRegistry

def get_current_time(timezone_offset: int = 8) -> str:
    """系统内置工具：获取当前时间"""
    # 示例逻辑，默认获取东八区时间，可根据传入的 timezone_offset 动态调整
    now = datetime.now(timezone.utc)
    return f"当前的 UTC 时间是: {now.isoformat()}"

def register_builtin_tools():
    """将系统核心内置能力注册到全局能力中心"""
    registry = CapabilityRegistry()
    
    registry.register_tool(
        name="get_current_time",
        description="获取当前的系统标准时间，如果用户询问时间日期，必须调用此工具。",
        func=get_current_time,
        parameters={
            "type": "object",
            "properties": {
                "timezone_offset": {
                    "type": "integer",
                    "description": "时区偏移量，例如东八区为 8"
                }
            },
            "required": []
        }
    )