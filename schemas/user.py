from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """用户注册时的请求模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名，需唯一")
    password: str = Field(..., min_length=6, description="明文密码，服务器会将其加密存储")

class UserLogin(BaseModel):
    """用户登录时的请求模型"""
    username: str
    password: str

class UserInfo(BaseModel):
    """脱敏后的用户信息响应模型"""
    id: str
    username: str
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        # 允许从 SQLAlchemy ORM 对象直接转换为此 Pydantic 模型
        from_attributes = True