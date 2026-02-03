"""
数据字典模块
"""

from fastapi import APIRouter
from app.api.v1.system.dict.controller import router

__all__ = ["router"]
