from sqlalchemy import Column, String, Text, DateTime, JSON, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    """物理表：用户信息"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ChatHistory(Base):
    """物理表：系统聊天记录落盘"""
    __tablename__ = "chat_history"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), index=True, nullable=False)
    user_id = Column(String(36), index=True, nullable=False)
    role = Column(String(20), nullable=False) # system, user, assistant, tool
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True) # 存储耗时、Token等元数据
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))