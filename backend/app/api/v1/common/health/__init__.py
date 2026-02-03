"""
健康检查模块
"""

from fastapi import APIRouter
from app.api.v1.common.health.controller import router

__all__ = ["router"]
