"""
监控模块
"""

from fastapi import APIRouter
from .server import router as server_router
from .online import router as online_router

# 创建监控路由
router = APIRouter()

# 注册子路由
router.include_router(server_router, prefix="/server", tags=["服务器监控"])
router.include_router(online_router, prefix="/online", tags=["在线用户"])

__all__ = ["router"]
