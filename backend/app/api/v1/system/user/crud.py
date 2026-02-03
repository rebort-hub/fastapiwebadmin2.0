"""
用户数据访问层
"""

from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.base_crud import BaseCRUD
from app.api.v1.system.user.model import UserModel


class UserCRUD(BaseCRUD[UserModel]):
    """用户CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(UserModel, db)
    
    async def get_by_username_crud(self, username: str) -> Optional[UserModel]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            用户实例或None
        """
        stmt = select(self.model).where(self.model.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_email_crud(self, email: str) -> Optional[UserModel]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱
            
        Returns:
            用户实例或None
        """
        stmt = select(self.model).where(self.model.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_phone_crud(self, phone: str) -> Optional[UserModel]:
        """
        根据手机号获取用户
        
        Args:
            phone: 手机号
            
        Returns:
            用户实例或None
        """
        stmt = select(self.model).where(self.model.phone == phone)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def check_username_exists_crud(
        self,
        username: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        检查用户名是否存在
        
        Args:
            username: 用户名
            exclude_id: 排除的用户ID（用于更新时检查）
            
        Returns:
            是否存在
        """
        stmt = select(self.model).where(self.model.username == username)
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def check_email_exists_crud(
        self,
        email: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        检查邮箱是否存在
        
        Args:
            email: 邮箱
            exclude_id: 排除的用户ID（用于更新时检查）
            
        Returns:
            是否存在
        """
        stmt = select(self.model).where(self.model.email == email)
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def check_phone_exists_crud(
        self,
        phone: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        检查手机号是否存在
        
        Args:
            phone: 手机号
            exclude_id: 排除的用户ID（用于更新时检查）
            
        Returns:
            是否存在
        """
        stmt = select(self.model).where(self.model.phone == phone)
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def update_password_crud(self, user_id: int, hashed_password: str) -> None:
        """
        更新用户密码
        
        Args:
            user_id: 用户ID
            hashed_password: 加密后的密码
        """
        await self.update_crud(user_id, {"password": hashed_password})
    
    async def update_login_info_crud(
        self,
        user_id: int,
        login_time: any,
        login_ip: str
    ) -> None:
        """
        更新登录信息
        
        Args:
            user_id: 用户ID
            login_time: 登录时间（datetime对象或字符串）
            login_ip: 登录IP
        """
        from datetime import datetime
        
        # 如果login_time是datetime对象，直接使用；否则转换
        if isinstance(login_time, datetime):
            login_time_value = login_time
        else:
            login_time_value = datetime.fromisoformat(str(login_time))
        
        await self.update_crud(user_id, {
            "last_login_time": login_time_value,
            "last_login_ip": login_ip
        })
