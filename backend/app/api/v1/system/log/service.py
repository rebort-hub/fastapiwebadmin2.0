"""
日志业务逻辑层
"""

import json
import time
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from user_agents import parse
from app.api.v1.system.log.crud import OperationLogCRUD, LoginLogCRUD
from app.api.v1.system.log.model import OperationLogModel, LoginLogModel
from app.api.v1.system.log.schema import (
    OperationLogCreateSchema,
    OperationLogOutSchema,
    OperationLogQuerySchema,
    LoginLogCreateSchema,
    LoginLogOutSchema,
    LoginLogQuerySchema,
    LogBatchDeleteSchema
)
from app.common.response import page_response


class LogService:
    """日志服务"""
    
    @staticmethod
    def get_client_ip(request: Request) -> str:
        """获取客户端IP地址"""
        # 优先从代理头获取真实IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 从连接信息获取
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return "unknown"
    
    @staticmethod
    def parse_user_agent(user_agent: str) -> dict:
        """解析用户代理信息"""
        if not user_agent:
            return {"browser": "unknown", "os": "unknown"}
        
        try:
            ua = parse(user_agent)
            return {
                "browser": f"{ua.browser.family} {ua.browser.version_string}",
                "os": f"{ua.os.family} {ua.os.version_string}"
            }
        except Exception:
            return {"browser": "unknown", "os": "unknown"}
    
    @staticmethod
    def get_location_by_ip(ip: str) -> str:
        """根据IP获取地理位置（简单实现）"""
        # 这里可以集成第三方IP定位服务
        if ip in ["127.0.0.1", "localhost", "::1"]:
            return "本地"
        return "未知"


class OperationLogService:
    """操作日志服务"""
    
    @classmethod
    async def create_operation_log(
        cls,
        request: Request,
        operation: str,
        module: str = None,
        description: str = None,
        user_id: int = None,
        username: str = None,
        request_data: dict = None,
        response_data: dict = None,
        status: int = 1,
        error_msg: str = None,
        execution_time: int = None,
        db: AsyncSession = None
    ) -> OperationLogModel:
        """创建操作日志"""
        crud = OperationLogCRUD(db)
        
        # 获取请求信息
        ip = LogService.get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        location = LogService.get_location_by_ip(ip)
        
        # 准备日志数据
        log_data = {
            "user_id": user_id,
            "username": username,
            "operation": operation,
            "method": request.method,
            "url": str(request.url),
            "ip": ip,
            "location": location,
            "user_agent": user_agent,
            "module": module,
            "description": description,
            "request_data": request_data,
            "response_data": response_data,
            "status": status,
            "error_msg": error_msg,
            "execution_time": execution_time,
            "operation_time": datetime.now(),
            "creation_date": datetime.now(),
            "updation_date": datetime.now()
        }
        
        return await crud.create_log(log_data)
    
    @classmethod
    async def get_operation_log_list(
        cls,
        query: OperationLogQuerySchema,
        db: AsyncSession
    ) -> dict:
        """获取操作日志列表"""
        crud = OperationLogCRUD(db)
        
        # 构建查询条件
        conditions = []
        if query.username:
            conditions.append(OperationLogModel.username.like(f"%{query.username}%"))
        if query.operation:
            conditions.append(OperationLogModel.operation.like(f"%{query.operation}%"))
        if query.method:
            conditions.append(OperationLogModel.method == query.method)
        if query.module:
            conditions.append(OperationLogModel.module.like(f"%{query.module}%"))
        if query.status is not None:
            conditions.append(OperationLogModel.status == query.status)
        if query.ip:
            conditions.append(OperationLogModel.ip.like(f"%{query.ip}%"))
        if query.begin_time:
            conditions.append(OperationLogModel.operation_time >= query.begin_time)
        if query.end_time:
            conditions.append(OperationLogModel.operation_time <= query.end_time)
        
        # 排序
        order_by = [OperationLogModel.operation_time.desc()]
        
        # 查询数据
        items, total = await crud.get_logs_by_conditions(
            conditions=conditions,
            order_by=order_by,
            skip=query.skip,
            limit=query.limit
        )
        
        # 转换为输出格式
        log_list = []
        for log_obj in items:
            log_dict = {c.name: getattr(log_obj, c.name) for c in log_obj.__table__.columns}
            log_data = OperationLogOutSchema.model_validate(log_dict)
            log_list.append(log_data.model_dump())
        
        return page_response(
            items=log_list,
            total=total,
            page=query.page,
            page_size=query.page_size
        )
    
    @classmethod
    async def get_operation_log_detail(
        cls,
        log_id: int,
        db: AsyncSession
    ) -> OperationLogOutSchema:
        """获取操作日志详情"""
        crud = OperationLogCRUD(db)
        log_obj = await crud.get_by_id_crud(log_id)
        
        if not log_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="日志不存在"
            )
        
        log_dict = {c.name: getattr(log_obj, c.name) for c in log_obj.__table__.columns}
        return OperationLogOutSchema.model_validate(log_dict)
    
    @classmethod
    async def delete_operation_logs(
        cls,
        data: LogBatchDeleteSchema,
        db: AsyncSession
    ) -> None:
        """批量删除操作日志"""
        crud = OperationLogCRUD(db)
        await crud.delete_logs_by_ids(data.ids)
    
    @classmethod
    async def clean_old_operation_logs(
        cls,
        days: int,
        db: AsyncSession
    ) -> int:
        """清理旧的操作日志"""
        crud = OperationLogCRUD(db)
        before_date = datetime.now() - timedelta(days=days)
        return await crud.delete_logs_before_date(before_date)
    
    @classmethod
    async def get_operation_log_statistics(
        cls,
        db: AsyncSession
    ) -> dict:
        """获取操作日志统计"""
        crud = OperationLogCRUD(db)
        return await crud.get_log_statistics()


class LoginLogService:
    """登录日志服务"""
    
    @classmethod
    async def create_login_log(
        cls,
        request: Request,
        username: str,
        user_id: int = None,
        login_type: str = "web",
        status: int = 1,
        message: str = None,
        db: AsyncSession = None
    ) -> LoginLogModel:
        """创建登录日志"""
        crud = LoginLogCRUD(db)
        
        # 获取请求信息
        ip = LogService.get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        location = LogService.get_location_by_ip(ip)
        ua_info = LogService.parse_user_agent(user_agent)
        
        # 准备日志数据
        log_data = {
            "user_id": user_id,
            "username": username,
            "login_type": login_type,
            "ip": ip,
            "location": location,
            "user_agent": user_agent,
            "browser": ua_info["browser"],
            "os": ua_info["os"],
            "status": status,
            "message": message,
            "login_time": datetime.now(),
            "creation_date": datetime.now(),
            "updation_date": datetime.now()
        }
        
        return await crud.create_log(log_data)
    
    @classmethod
    async def create_logout_log(
        cls,
        user_id: int,
        db: AsyncSession
    ) -> None:
        """记录用户退出"""
        crud = LoginLogCRUD(db)
        await crud.update_logout_time(user_id, datetime.now())
    
    @classmethod
    async def get_login_log_list(
        cls,
        query: LoginLogQuerySchema,
        db: AsyncSession
    ) -> dict:
        """获取登录日志列表"""
        crud = LoginLogCRUD(db)
        
        # 构建查询条件
        conditions = []
        if query.username:
            conditions.append(LoginLogModel.username.like(f"%{query.username}%"))
        if query.login_type:
            conditions.append(LoginLogModel.login_type == query.login_type)
        if query.status is not None:
            conditions.append(LoginLogModel.status == query.status)
        if query.ip:
            conditions.append(LoginLogModel.ip.like(f"%{query.ip}%"))
        if query.begin_time:
            conditions.append(LoginLogModel.login_time >= query.begin_time)
        if query.end_time:
            conditions.append(LoginLogModel.login_time <= query.end_time)
        
        # 排序
        order_by = [LoginLogModel.login_time.desc()]
        
        # 查询数据
        items, total = await crud.get_logs_by_conditions(
            conditions=conditions,
            order_by=order_by,
            skip=query.skip,
            limit=query.limit
        )
        
        # 转换为输出格式
        log_list = []
        for log_obj in items:
            log_dict = {c.name: getattr(log_obj, c.name) for c in log_obj.__table__.columns}
            log_data = LoginLogOutSchema.model_validate(log_dict)
            log_list.append(log_data.model_dump())
        
        return page_response(
            items=log_list,
            total=total,
            page=query.page,
            page_size=query.page_size
        )
    
    @classmethod
    async def get_login_log_detail(
        cls,
        log_id: int,
        db: AsyncSession
    ) -> LoginLogOutSchema:
        """获取登录日志详情"""
        crud = LoginLogCRUD(db)
        log_obj = await crud.get_by_id_crud(log_id)
        
        if not log_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="日志不存在"
            )
        
        log_dict = {c.name: getattr(log_obj, c.name) for c in log_obj.__table__.columns}
        return LoginLogOutSchema.model_validate(log_dict)
    
    @classmethod
    async def delete_login_logs(
        cls,
        data: LogBatchDeleteSchema,
        db: AsyncSession
    ) -> None:
        """批量删除登录日志"""
        crud = LoginLogCRUD(db)
        await crud.delete_logs_by_ids(data.ids)
    
    @classmethod
    async def clean_old_login_logs(
        cls,
        days: int,
        db: AsyncSession
    ) -> int:
        """清理旧的登录日志"""
        crud = LoginLogCRUD(db)
        before_date = datetime.now() - timedelta(days=days)
        return await crud.delete_logs_before_date(before_date)
    
    @classmethod
    async def get_login_log_statistics(
        cls,
        db: AsyncSession
    ) -> dict:
        """获取登录日志统计"""
        crud = LoginLogCRUD(db)
        return await crud.get_log_statistics()