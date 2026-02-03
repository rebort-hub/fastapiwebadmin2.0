"""
在线用户监控控制器
"""

from fastapi import APIRouter, Depends, Query
from app.common.response import success_response
from app.api.v1.monitor.online.service import OnlineUserService
from app.api.v1.system.auth.dependencies import get_current_user
from app.models.system_models import User

router = APIRouter()


@router.get("/users", summary="获取在线用户列表")
async def get_online_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user)
):
    """
    获取在线用户列表
    """
    result = await OnlineUserService.get_online_users(page, page_size)
    return success_response(data=result)


@router.get("/stats", summary="获取在线用户统计")
async def get_online_stats(current_user: User = Depends(get_current_user)):
    """
    获取在线用户统计信息
    """
    stats = await OnlineUserService.get_online_stats()
    return success_response(data=stats.dict())


@router.post("/force-offline/{user_id}", summary="强制用户下线")
async def force_user_offline(
    user_id: int,
    session_id: str = Query(None, description="会话ID，不传则下线所有会话"),
    current_user: User = Depends(get_current_user)
):
    """
    强制指定用户下线
    """
    result = await OnlineUserService.force_offline(user_id, session_id)
    if result:
        return success_response(message="用户已强制下线")
    else:
        return success_response(message="用户不在线或下线失败", code=400)


@router.post("/cleanup", summary="清理过期用户")
async def cleanup_expired_users(current_user: User = Depends(get_current_user)):
    """
    清理过期的在线用户
    """
    await OnlineUserService.cleanup_expired_users()
    return success_response(message="清理完成")