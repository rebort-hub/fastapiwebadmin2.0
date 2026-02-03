"""
文件管理模块
"""

from fastapi import APIRouter
from app.api.v1.common.file.controller import router

__all__ = ["router"]
