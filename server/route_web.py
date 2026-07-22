from fastapi import APIRouter, Depends
from schemas.user import UserInfo
from core.security.auth import require_admin
import logging

logger = logging.getLogger("TideBot")
router = APIRouter(prefix="/api/v1/web", tags=["Web Console"])

@router.get("/status")
async def get_system_status(current_admin: dict = Depends(require_admin)):
    """获取系统运行状态大盘数据 (仅管理员)"""
    return {
        "status": "running",
        "active_sessions": 12, # 模拟数据
        "total_memory_used_mb": 145,
        "operator": current_admin.get("user_id")
    }

@router.post("/reload_config")
async def reload_system_config(current_admin: dict = Depends(require_admin)):
    """热重载 config.yaml (仅管理员)"""
    from core.config_manager import ConfigManager
    try:
        ConfigManager().reload()
        return {"msg": "系统配置已热重载成功"}
    except Exception as e:
        return {"msg": f"重载失败: {str(e)}"}