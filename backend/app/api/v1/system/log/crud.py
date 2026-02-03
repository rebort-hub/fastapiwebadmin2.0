"""
日志CRUD操作
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_
from app.core.base_crud import BaseCRUD
from app.api.v1.system.log.model import OperationLogModel, LoginLogModel


class OperationLogCRUD(BaseCRUD[OperationLogModel]):
    """操作日志CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(OperationLogModel, db)
    
    async def create_log(self, log_data: dict) -> OperationLogModel:
        """创建操作日志"""
        return await self.create_crud(log_data)
    
    async def get_logs_by_conditions(
        self,
        conditions: List = None,
        order_by: List = None,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[OperationLogModel], int]:
        """根据条件查询操作日志"""
        return await self.get_list_crud(conditions, order_by, skip, limit)
    
    async def delete_logs_by_ids(self, ids: List[int]) -> None:
        """批量删除操作日志"""
        await self.delete_crud(ids)
    
    async def delete_logs_before_date(self, before_date: datetime) -> int:
        """删除指定日期之前的日志"""
        stmt = delete(self.model).where(self.model.operation_time < before_date)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount
    
    async def get_log_statistics(self) -> dict:
        """获取日志统计信息"""
        # 总日志数
        total_stmt = select(func.count(self.model.id))
        total_result = await self.db.execute(total_stmt)
        total_count = total_result.scalar()
        
        # 今日日志数
        today = datetime.now().date()
        today_stmt = select(func.count(self.model.id)).where(
            func.date(self.model.operation_time) == today
        )
        today_result = await self.db.execute(today_stmt)
        today_count = today_result.scalar()
        
        # 成功/失败统计
        success_stmt = select(func.count(self.model.id)).where(self.model.status == 1)
        success_result = await self.db.execute(success_stmt)
        success_count = success_result.scalar()
        
        failed_stmt = select(func.count(self.model.id)).where(self.model.status == 0)
        failed_result = await self.db.execute(failed_stmt)
        failed_count = failed_result.scalar()
        
        return {
            "total_count": total_count or 0,
            "today_count": today_count or 0,
            "success_count": success_count or 0,
            "failed_count": failed_count or 0
        }


class LoginLogCRUD(BaseCRUD[LoginLogModel]):
    """登录日志CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(LoginLogModel, db)
    
    async def create_log(self, log_data: dict) -> LoginLogModel:
        """创建登录日志"""
        return await self.create_crud(log_data)
    
    async def get_logs_by_conditions(
        self,
        conditions: List = None,
        order_by: List = None,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[LoginLogModel], int]:
        """根据条件查询登录日志"""
        return await self.get_list_crud(conditions, order_by, skip, limit)
    
    async def delete_logs_by_ids(self, ids: List[int]) -> None:
        """批量删除登录日志"""
        await self.delete_crud(ids)
    
    async def delete_logs_before_date(self, before_date: datetime) -> int:
        """删除指定日期之前的日志"""
        stmt = delete(self.model).where(self.model.login_time < before_date)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount
    
    async def update_logout_time(self, user_id: int, logout_time: datetime) -> None:
        """更新用户的退出时间"""
        # 找到最近的登录记录并更新退出时间
        stmt = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.status == 1,
                self.model.logout_time.is_(None)
            )
        ).order_by(self.model.login_time.desc()).limit(1)
        
        result = await self.db.execute(stmt)
        login_log = result.scalar_one_or_none()
        
        if login_log:
            login_log.logout_time = logout_time
            await self.db.commit()
    
    async def get_login_statistics(self) -> dict:
        """获取登录统计信息"""
        # 总登录次数
        total_stmt = select(func.count(self.model.id))
        total_result = await self.db.execute(total_stmt)
        total_count = total_result.scalar()
        
        # 今日登录次数
        today = datetime.now().date()
        today_stmt = select(func.count(self.model.id)).where(
            func.date(self.model.login_time) == today
        )
        today_result = await self.db.execute(today_stmt)
        today_count = today_result.scalar()
        
        # 成功/失败统计
        success_stmt = select(func.count(self.model.id)).where(self.model.status == 1)
        success_result = await self.db.execute(success_stmt)
        success_count = success_result.scalar()
        
        failed_stmt = select(func.count(self.model.id)).where(self.model.status == 0)
        failed_result = await self.db.execute(failed_stmt)
        failed_count = failed_result.scalar()
        
        return {
            "total_count": total_count or 0,
            "today_count": today_count or 0,
            "success_count": success_count or 0,
            "failed_count": failed_count or 0
        }