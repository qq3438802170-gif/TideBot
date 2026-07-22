from pydantic import BaseModel, Field
from typing import Optional

class SystemConfigUpdate(BaseModel):
    """
    提供给 Admin 面板用于热更新系统配置的模型
    仅允许更新部分非致命业务参数
    """
    default_model: Optional[str] = Field(None, description="全局默认大模型名称")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="大模型温度参数 (0-2)")
    memory_window_size: Optional[int] = Field(None, ge=1, le=100, description="滑动记忆窗口大小")