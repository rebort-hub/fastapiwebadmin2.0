"""
部门数据访问层
"""

from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.base_crud import BaseCRUD
from app.api.v1.system.dept.model import DeptModel


class DeptCRUD(BaseCRUD[DeptModel]):
    """部门CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(DeptModel, db)
    
    async def get_by_name_crud(self, dept_name: str) -> Optional[DeptModel]:
        """
        根据部门名称获取部门
        
        Args:
            dept_name: 部门名称
            
        Returns:
            部门实例或None
        """
        stmt = select(self.model).where(self.model.dept_name == dept_name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_code_crud(self, dept_code: str) -> Optional[DeptModel]:
        """
        根据部门编码获取部门
        
        Args:
            dept_code: 部门编码
            
        Returns:
            部门实例或None
        """
        stmt = select(self.model).where(self.model.dept_code == dept_code)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def check_name_exists_crud(
        self,
        dept_name: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        检查部门名称是否存在
        
        Args:
            dept_name: 部门名称
            exclude_id: 排除的部门ID（用于更新时检查）
            
        Returns:
            是否存在
        """
        stmt = select(self.model).where(self.model.dept_name == dept_name)
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def check_code_exists_crud(
        self,
        dept_code: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        检查部门编码是否存在
        
        Args:
            dept_code: 部门编码
            exclude_id: 排除的部门ID（用于更新时检查）
            
        Returns:
            是否存在
        """
        if not dept_code:
            return False
        stmt = select(self.model).where(self.model.dept_code == dept_code)
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def get_children_crud(self, parent_id: int) -> List[DeptModel]:
        """
        获取子部门列表
        
        Args:
            parent_id: 父部门ID
            
        Returns:
            子部门列表
        """
        stmt = select(self.model).where(
            self.model.parent_id == parent_id
        ).order_by(self.model.sort.asc(), self.model.id.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_all_children_crud(self, parent_id: int) -> List[DeptModel]:
        """
        递归获取所有子部门（包括子部门的子部门）
        
        Args:
            parent_id: 父部门ID
            
        Returns:
            所有子部门列表
        """
        all_children = []
        
        # 获取直接子部门
        children = await self.get_children_crud(parent_id)
        
        for child in children:
            all_children.append(child)
            # 递归获取子部门的子部门
            sub_children = await self.get_all_children_crud(child.id)
            all_children.extend(sub_children)
        
        return all_children
    
    async def get_all_depts_crud(self) -> List[DeptModel]:
        """
        获取所有部门列表（按排序）
        
        Returns:
            所有部门列表
        """
        stmt = select(self.model).order_by(
            self.model.sort.asc(),
            self.model.id.asc()
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def has_children_crud(self, dept_id: int) -> bool:
        """
        检查部门是否有子部门
        
        Args:
            dept_id: 部门ID
            
        Returns:
            是否有子部门
        """
        stmt = select(self.model).where(self.model.parent_id == dept_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def get_user_count_crud(self, dept_id: int) -> int:
        """
        获取部门下的用户数量
        
        Args:
            dept_id: 部门ID
            
        Returns:
            用户数量
        """
        from app.api.v1.system.user.model import UserModel
        from sqlalchemy import func
        
        stmt = select(func.count(UserModel.id)).where(
            UserModel.dept_id == dept_id
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
