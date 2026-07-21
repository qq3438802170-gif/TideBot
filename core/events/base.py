from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid

class BaseEvent(BaseModel):
    """
    系统事件的绝对基类
    所有在事件总线中流通的事件必须继承此类
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        arbitrary_types_allowed = True