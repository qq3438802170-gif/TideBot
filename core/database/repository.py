from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database.models import User, ChatHistory
from typing import List, Optional

class UserRepository:
    """用户表的数据仓库操作"""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def create_user(self, username: str, hashed_password: Optional[str] = None) -> User:
        new_user = User(username=username, hashed_password=hashed_password)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

class ChatHistoryRepository:
    """聊天记录表的数据仓库操作"""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_message(self, session_id: str, user_id: str, role: str, content: str, meta: dict = None) -> ChatHistory:
        msg = ChatHistory(
            session_id=session_id,
            user_id=user_id,
            role=role,
            content=content,
            metadata_json=meta
        )
        self.session.add(msg)
        await self.session.commit()
        return msg

    async def get_session_history(self, session_id: str, limit: int = 50) -> List[ChatHistory]:
        # 按时间倒序查询，并限制条数
        stmt = select(ChatHistory).where(ChatHistory.session_id == session_id).order_by(ChatHistory.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        # 将结果反转回时间正序
        return list(result.scalars().all())[::-1]