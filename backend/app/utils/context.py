# -*- coding: utf-8 -*-
# @author: rebort
"""
上下文变量管理

保留必要的上下文变量，移除已弃用的AccessToken
"""
from contextvars import ContextVar
from typing import Optional

from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

# 应用追踪ID - 用于日志追踪
AppTraceId: ContextVar[Optional[str]] = ContextVar('AppTraceId', default=None)

# 数据库会话 - 用于事务管理
SQLAlchemySession: ContextVar[Optional[AsyncSession]] = ContextVar('SQLAlchemySession', default=None)

# FastAPI请求对象 - 用于获取请求信息
FastApiRequest: ContextVar[Optional[Request]] = ContextVar('fastApiRequest', default=None)
