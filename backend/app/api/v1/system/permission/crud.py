"""
权限数据访问层
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.base_crud import BaseCRUD
from app.api.v1.system.permission.model import PermissionModel


class PermissionCRUD(BaseCRUD[PermissionModel]):
    """权限CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(PermissionModel, db)
    
    async def get_by_code_crud(self, permission_code: str) -> Optional[PermissionModel]:
        """根据权限编码获取"""
        stmt = select(self.model).where(self.model.permission_code == permission_code)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def check_code_exists_crud(
        self,
        permission_code: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """检查权限编码是否存在"""
        stmt = select(self.model).where(self.model.permission_code == permission_code)
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def get_by_type_crud(self, permission_type: int) -> List[PermissionModel]:
        """根据权限类型获取"""
        stmt = select(self.model).where(
            self.model.permission_type == permission_type,
            self.model.status == 1
        ).order_by(self.model.sort.asc(), self.model.id.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_codes_crud(self, permission_codes: List[str]) -> List[PermissionModel]:
        """根据权限编码列表获取"""
        stmt = select(self.model).where(
            self.model.permission_code.in_(permission_codes),
            self.model.status == 1
        ).order_by(self.model.sort.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
