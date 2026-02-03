"""
菜单数据访问层
"""

from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.base_crud import BaseCRUD
from app.api.v1.system.menu.model import MenuModel


class MenuCRUD(BaseCRUD[MenuModel]):
    """菜单CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(MenuModel, db)
    
    async def get_by_name_crud(self, menu_name: str) -> Optional[MenuModel]:
        """
        根据菜单名称获取菜单
        
        Args:
            menu_name: 菜单名称
            
        Returns:
            菜单实例或None
        """
        stmt = select(self.model).where(self.model.menu_name == menu_name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_perms_crud(self, perms: str) -> Optional[MenuModel]:
        """
        根据权限标识获取菜单
        
        Args:
            perms: 权限标识
            
        Returns:
            菜单实例或None
        """
        stmt = select(self.model).where(self.model.perms == perms)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def check_name_exists_crud(
        self,
        menu_name: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        检查菜单名称是否存在
        
        Args:
            menu_name: 菜单名称
            exclude_id: 排除的菜单ID（用于更新时检查）
            
        Returns:
            是否存在
        """
        stmt = select(self.model).where(self.model.menu_name == menu_name)
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def check_perms_exists_crud(
        self,
        perms: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        检查权限标识是否存在
        
        Args:
            perms: 权限标识
            exclude_id: 排除的菜单ID（用于更新时检查）
            
        Returns:
            是否存在
        """
        if not perms:
            return False
        stmt = select(self.model).where(self.model.perms == perms)
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def get_children_crud(self, parent_id: int) -> List[MenuModel]:
        """
        获取子菜单列表
        
        Args:
            parent_id: 父菜单ID
            
        Returns:
            子菜单列表
        """
        stmt = select(self.model).where(
            self.model.parent_id == parent_id
        ).order_by(self.model.order_num.asc(), self.model.id.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_all_children_crud(self, parent_id: int) -> List[MenuModel]:
        """
        递归获取所有子菜单
        
        Args:
            parent_id: 父菜单ID
            
        Returns:
            所有子菜单列表
        """
        all_children = []
        children = await self.get_children_crud(parent_id)
        
        for child in children:
            all_children.append(child)
            sub_children = await self.get_all_children_crud(child.id)
            all_children.extend(sub_children)
        
        return all_children
    
    async def get_all_menus_crud(self) -> List[MenuModel]:
        """
        获取所有菜单列表（按排序）
        
        Returns:
            所有菜单列表
        """
        stmt = select(self.model).order_by(
            self.model.order_num.asc(),
            self.model.id.asc()
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_menus_by_type_crud(self, menu_type: int) -> List[MenuModel]:
        """
        根据菜单类型获取菜单列表
        
        Args:
            menu_type: 菜单类型（1:目录 2:菜单 3:按钮）
            
        Returns:
            菜单列表
        """
        stmt = select(self.model).where(
            self.model.menu_type == menu_type
        ).order_by(self.model.order_num.asc(), self.model.id.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_menus_by_ids_crud(self, menu_ids: List[int]) -> List[MenuModel]:
        """
        根据ID列表获取菜单
        
        Args:
            menu_ids: 菜单ID列表
            
        Returns:
            菜单列表
        """
        stmt = select(self.model).where(
            self.model.id.in_(menu_ids)
        ).order_by(self.model.order_num.asc(), self.model.id.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def has_children_crud(self, menu_id: int) -> bool:
        """
        检查菜单是否有子菜单
        
        Args:
            menu_id: 菜单ID
            
        Returns:
            是否有子菜单
        """
        stmt = select(self.model).where(self.model.parent_id == menu_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
