"""
角色数据访问层
"""

from typing import Optional, List
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.base_crud import BaseCRUD
from app.api.v1.system.role.model import RoleModel


class RoleCRUD(BaseCRUD[RoleModel]):
    """角色CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(RoleModel, db)
    
    async def get_by_name_crud(self, role_name: str) -> Optional[RoleModel]:
        """
        根据角色名称获取角色
        
        Args:
            role_name: 角色名称
            
        Returns:
            角色实例或None
        """
        stmt = select(self.model).where(self.model.role_name == role_name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_key_crud(self, role_key: str) -> Optional[RoleModel]:
        """
        根据角色权限字符串获取角色
        
        Args:
            role_key: 角色权限字符串
            
        Returns:
            角色实例或None
        """
        stmt = select(self.model).where(self.model.role_key == role_key)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def check_name_exists_crud(
        self,
        role_name: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        检查角色名称是否存在
        
        Args:
            role_name: 角色名称
            exclude_id: 排除的角色ID（用于更新时检查）
            
        Returns:
            是否存在
        """
        stmt = select(self.model).where(self.model.role_name == role_name)
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def check_key_exists_crud(
        self,
        role_key: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        检查角色权限字符串是否存在
        
        Args:
            role_key: 角色权限字符串
            exclude_id: 排除的角色ID（用于更新时检查）
            
        Returns:
            是否存在
        """
        stmt = select(self.model).where(self.model.role_key == role_key)
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def get_user_count_crud(self, role_id: int) -> int:
        """
        获取角色关联的用户数量
        
        Args:
            role_id: 角色ID
            
        Returns:
            用户数量
        """
        role = await self.get_by_id_crud(role_id)
        if role and hasattr(role, 'users'):
            return len(role.users)
        return 0
