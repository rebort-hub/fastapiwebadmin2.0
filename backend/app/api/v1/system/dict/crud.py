"""
数据字典数据访问层
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.base_crud import BaseCRUD
from app.api.v1.system.dict.model import DictTypeModel, DictDataModel


class DictTypeCRUD(BaseCRUD[DictTypeModel]):
    """字典类型CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(DictTypeModel, db)
    
    async def get_by_type_crud(self, dict_type: str) -> Optional[DictTypeModel]:
        """根据字典类型获取"""
        stmt = select(self.model).where(self.model.dict_type == dict_type)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def check_type_exists_crud(
        self,
        dict_type: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """检查字典类型是否存在"""
        stmt = select(self.model).where(self.model.dict_type == dict_type)
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None


class DictDataCRUD(BaseCRUD[DictDataModel]):
    """字典数据CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(DictDataModel, db)
    
    async def get_by_type_crud(self, dict_type: str) -> List[DictDataModel]:
        """根据字典类型获取所有数据"""
        stmt = select(self.model).where(
            self.model.dict_type == dict_type
        ).order_by(self.model.dict_sort.asc(), self.model.id.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def delete_by_type_crud(self, dict_type: str) -> None:
        """根据字典类型删除所有数据"""
        from sqlalchemy import delete
        stmt = delete(self.model).where(self.model.dict_type == dict_type)
        await self.db.execute(stmt)
        await self.db.commit()
