"""
API v1版本
"""

from fastapi import APIRouter
from app.api.v1.system import router as system_router
from app.api.v1.monitor import router as monitor_router
from app.api.v1.common.health.controller import router as health_router

# 创建v1路由
router = APIRouter(prefix="/v1")

# 注册子路由
router.include_router(system_router, prefix="/system", tags=["系统管理"])
router.include_router(monitor_router, prefix="/monitor", tags=["系统监控"])
router.include_router(health_router, prefix="/common/health", tags=["健康检查"])

__all__ = ["router"]
