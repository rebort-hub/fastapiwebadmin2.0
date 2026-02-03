"""
认证授权模块
"""

from fastapi import APIRouter
from app.api.v1.system.auth.controller import router

__all__ = ["router"]
