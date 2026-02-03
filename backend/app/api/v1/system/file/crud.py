"""
文件管理数据访问层
"""

from typing import Optional, List, Tuple
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.base_crud import BaseCRUD
from app.api.v1.system.file.model import FileModel


class FileCRUD(BaseCRUD[FileModel]):
    """文件CRUD"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(FileModel, db)
    
    async def get_by_file_name_crud(self, file_name: str) -> Optional[FileModel]:
        """
        根据文件名获取文件
        
        Args:
            file_name: 文件名
            
        Returns:
            文件实例或None
        """
        stmt = select(self.model).where(self.model.file_name == file_name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_file_path_crud(self, file_path: str) -> Optional[FileModel]:
        """
        根据文件路径获取文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件实例或None
        """
        stmt = select(self.model).where(self.model.file_path == file_path)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_files_crud(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[FileModel]:
        """
        获取用户上传的文件
        
        Args:
            user_id: 用户ID
            limit: 限制数量
            
        Returns:
            文件列表
        """
        stmt = (
            select(self.model)
            .where(self.model.uploaded_by == user_id)
            .order_by(self.model.creation_date.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_public_files_crud(
        self,
        limit: int = 10
    ) -> List[FileModel]:
        """
        获取公开文件
        
        Args:
            limit: 限制数量
            
        Returns:
            文件列表
        """
        stmt = (
            select(self.model)
            .where(self.model.is_public == 1)
            .order_by(self.model.creation_date.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def search_files_crud(
        self,
        keyword: str,
        user_id: Optional[int] = None,
        is_public: Optional[int] = None,
        limit: int = 50
    ) -> List[FileModel]:
        """
        搜索文件
        
        Args:
            keyword: 搜索关键词
            user_id: 用户ID（可选）
            is_public: 是否公开（可选）
            limit: 限制数量
            
        Returns:
            文件列表
        """
        conditions = [
            or_(
                self.model.original_name.like(f"%{keyword}%"),
                self.model.description.like(f"%{keyword}%"),
                self.model.tags.like(f"%{keyword}%")
            )
        ]
        
        if user_id is not None:
            conditions.append(self.model.uploaded_by == user_id)
        
        if is_public is not None:
            conditions.append(self.model.is_public == is_public)
        
        stmt = (
            select(self.model)
            .where(and_(*conditions))
            .order_by(self.model.creation_date.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def increment_download_count_crud(self, file_id: int) -> None:
        """
        增加下载次数
        
        Args:
            file_id: 文件ID
        """
        file_obj = await self.get_by_id_crud(file_id)
        if file_obj:
            await self.update_crud(file_id, {
                "download_count": file_obj.download_count + 1
            })
    
    async def get_files_by_type_crud(
        self,
        file_ext: str,
        limit: int = 10
    ) -> List[FileModel]:
        """
        根据文件类型获取文件
        
        Args:
            file_ext: 文件扩展名
            limit: 限制数量
            
        Returns:
            文件列表
        """
        stmt = (
            select(self.model)
            .where(self.model.file_ext == file_ext)
            .order_by(self.model.creation_date.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_large_files_crud(
        self,
        min_size: int,
        limit: int = 10
    ) -> List[FileModel]:
        """
        获取大文件
        
        Args:
            min_size: 最小文件大小（字节）
            limit: 限制数量
            
        Returns:
            文件列表
        """
        stmt = (
            select(self.model)
            .where(self.model.file_size >= min_size)
            .order_by(self.model.file_size.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_files_stats_crud(self) -> dict:
        """
        获取文件统计信息
        
        Returns:
            统计信息字典
        """
        from sqlalchemy import func
        
        # 总文件数
        total_count_stmt = select(func.count(self.model.id))
        total_count_result = await self.db.execute(total_count_stmt)
        total_count = total_count_result.scalar()
        
        # 总文件大小
        total_size_stmt = select(func.sum(self.model.file_size))
        total_size_result = await self.db.execute(total_size_stmt)
        total_size = total_size_result.scalar() or 0
        
        # 公开文件数
        public_count_stmt = select(func.count(self.model.id)).where(self.model.is_public == 1)
        public_count_result = await self.db.execute(public_count_stmt)
        public_count = public_count_result.scalar()
        
        # 私有文件数
        private_count = total_count - public_count
        
        return {
            "total_count": total_count,
            "total_size": total_size,
            "public_count": public_count,
            "private_count": private_count
        }