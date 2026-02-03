"""
用户管理模块
"""

from fastapi import APIRouter
from app.api.v1.system.user.controller import router

__all__ = ["router"]
