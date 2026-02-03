"""
日志数据验证模型
"""

from typing import Optional, Any
from datetime import datetime
from pydantic import Field
from app.core.base_schema import BaseSchema, PageQuerySchema, TimestampSchema


class OperationLogCreateSchema(BaseSchema):
    """操作日志创建Schema"""
    
    user_id: Optional[int] = Field(None, description="操作用户ID")
    username: Optional[str] = Field(None, description="操作用户名")
    operation: str = Field(..., description="操作类型")
    method: str = Field(..., description="请求方法")
    url: str = Field(..., description="请求URL")
    ip: Optional[str] = Field(None, description="操作IP")
    location: Optional[str] = Field(None, description="操作地点")
    user_agent: Optional[str] = Field(None, description="用户代理")
    
    module: Optional[str] = Field(None, description="操作模块")
    description: Optional[str] = Field(None, description="操作描述")
    request_data: Optional[Any] = Field(None, description="请求参数")
    response_data: Optional[Any] = Field(None, description="响应数据")
    
    status: int = Field(1, description="操作状态")
    error_msg: Optional[str] = Field(None, description="错误信息")
    execution_time: Optional[int] = Field(None, description="执行时间")
    
    operation_time: datetime = Field(..., description="操作时间")


class OperationLogOutSchema(TimestampSchema):
    """操作日志输出Schema"""
    
    id: int = Field(..., description="日志ID")
    user_id: Optional[int] = Field(None, description="操作用户ID")
    username: Optional[str] = Field(None, description="操作用户名")
    operation: str = Field(..., description="操作类型")
    method: str = Field(..., description="请求方法")
    url: str = Field(..., description="请求URL")
    ip: Optional[str] = Field(None, description="操作IP")
    location: Optional[str] = Field(None, description="操作地点")
    user_agent: Optional[str] = Field(None, description="用户代理")
    
    module: Optional[str] = Field(None, description="操作模块")
    description: Optional[str] = Field(None, description="操作描述")
    request_data: Optional[Any] = Field(None, description="请求参数")
    response_data: Optional[Any] = Field(None, description="响应数据")
    
    status: int = Field(..., description="操作状态")
    error_msg: Optional[str] = Field(None, description="错误信息")
    execution_time: Optional[int] = Field(None, description="执行时间")
    
    operation_time: datetime = Field(..., description="操作时间")


class OperationLogQuerySchema(PageQuerySchema):
    """操作日志查询Schema"""
    
    username: Optional[str] = Field(None, description="用户名（模糊查询）")
    operation: Optional[str] = Field(None, description="操作类型")
    method: Optional[str] = Field(None, description="请求方法")
    module: Optional[str] = Field(None, description="操作模块")
    status: Optional[int] = Field(None, description="操作状态")
    ip: Optional[str] = Field(None, description="操作IP")
    begin_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")


class LoginLogCreateSchema(BaseSchema):
    """登录日志创建Schema"""
    
    user_id: Optional[int] = Field(None, description="用户ID")
    username: str = Field(..., description="用户名")
    login_type: str = Field("web", description="登录类型")
    
    ip: Optional[str] = Field(None, description="登录IP")
    location: Optional[str] = Field(None, description="登录地点")
    user_agent: Optional[str] = Field(None, description="用户代理")
    browser: Optional[str] = Field(None, description="浏览器")
    os: Optional[str] = Field(None, description="操作系统")
    
    status: int = Field(..., description="登录状态")
    message: Optional[str] = Field(None, description="登录信息")
    
    login_time: datetime = Field(..., description="登录时间")
    logout_time: Optional[datetime] = Field(None, description="退出时间")


class LoginLogOutSchema(TimestampSchema):
    """登录日志输出Schema"""
    
    id: int = Field(..., description="日志ID")
    user_id: Optional[int] = Field(None, description="用户ID")
    username: str = Field(..., description="用户名")
    login_type: str = Field(..., description="登录类型")
    
    ip: Optional[str] = Field(None, description="登录IP")
    location: Optional[str] = Field(None, description="登录地点")
    user_agent: Optional[str] = Field(None, description="用户代理")
    browser: Optional[str] = Field(None, description="浏览器")
    os: Optional[str] = Field(None, description="操作系统")
    
    status: int = Field(..., description="登录状态")
    message: Optional[str] = Field(None, description="登录信息")
    
    login_time: datetime = Field(..., description="登录时间")
    logout_time: Optional[datetime] = Field(None, description="退出时间")


class LoginLogQuerySchema(PageQuerySchema):
    """登录日志查询Schema"""
    
    username: Optional[str] = Field(None, description="用户名（模糊查询）")
    login_type: Optional[str] = Field(None, description="登录类型")
    status: Optional[int] = Field(None, description="登录状态")
    ip: Optional[str] = Field(None, description="登录IP")
    begin_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")


class LogBatchDeleteSchema(BaseSchema):
    """日志批量删除Schema"""
    
    ids: list[int] = Field(..., description="日志ID列表")