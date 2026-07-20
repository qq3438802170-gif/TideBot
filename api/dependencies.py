from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from env import settings

# 规定标准的令牌提取终点
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# 为保证 API 能够独立调试，在底层基础设施实现前，声明业务层所需的纯净实体
class CurrentUserDomain(BaseModel):
    id: str
    username: str
    is_active: bool
    role: str

async def get_db() -> AsyncGenerator[None, None]:
    """
    异步数据库 Session 生命周期注入器 (Clean Architecture 边界守卫)[cite: 6]
    """
    # TODO: 后续迭代中在此处导入并承载 infrastructure/database.py 的 async_session
    print("[Debug DB Scope] 异步上下文生存期初始化开始")
    try:
        yield None
    finally:
        print("[Debug DB Scope] 异步上下文执行完毕，安全释放连接")

async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> CurrentUserDomain:
    """
    基于 JWT 算法的高性能分布式鉴权依赖项
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证凭证已失效或无法通过安全校验",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        username: Optional[str] = payload.get("username")
        role: Optional[str] = payload.get("role", "user")
        if user_id is None or username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 返回纯业务实体模型，与底层具体的数据库实体隔离
    return CurrentUserDomain(
        id=user_id,
        username=username,
        is_active=True,
        role=role
    )

async def require_admin_privilege(
    current_user: CurrentUserDomain = Depends(get_current_user)
) -> CurrentUserDomain:
    """
    高阶管理控制台动态权限守卫
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，当前安全边界仅对系统管理员开放"
        )
    return current_user