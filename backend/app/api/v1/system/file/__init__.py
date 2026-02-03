"""
文件管理模块
"""

from fastapi import APIRouter
from app.api.v1.system.file.controller import router

__all__ = ["router"]