"""
权限业务逻辑层
"""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.v1.system.permission.crud import PermissionCRUD
from app.api.v1.system.permission.schema import (
    PermissionCreateSchema,
    PermissionUpdateSchema,
    PermissionOutSchema,
    PermissionQuerySchema
)
from app.api.v1.system.permission.model import PermissionModel
from app.common.response import page_response, success_response


class PermissionService:
    """权限服务"""
    
    @classmethod
    async def get_permission_detail_service(
        cls,
        permission_id: int,
        db: AsyncSession
    ) -> PermissionOutSchema:
        """获取权限详情"""
        crud = PermissionCRUD(db)
        permission = await crud.get_by_id_crud(permission_id)
        
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="权限不存在"
            )
        
        return PermissionOutSchema.model_validate(permission)
    
    @classmethod
    async def get_permission_list_service(
        cls,
        query: PermissionQuerySchema,
        db: AsyncSession
    ) -> dict:
        """获取权限列表"""
        crud = PermissionCRUD(db)
        
        # 构建查询条件
        conditions = []
        if query.permission_name:
            conditions.append(PermissionModel.permission_name.like(f"%{query.permission_name}%"))
        if query.permission_code:
            conditions.append(PermissionModel.permission_code.like(f"%{query.permission_code}%"))
        if query.permission_type:
            conditions.append(PermissionModel.permission_type == query.permission_type)
        if query.status is not None:
            conditions.append(PermissionModel.status == query.status)
        
        # 排序
        order_by = [PermissionModel.id.asc()]
        
        # 查询数据
        items, total = await crud.get_list_crud(
            conditions=conditions,
            order_by=order_by,
            skip=query.skip,
            limit=query.limit
        )
        
        # 转换为输出格式
        permission_list = [
            PermissionOutSchema.model_validate(item).model_dump()
            for item in items
        ]
        
        return page_response(
            items=permission_list,
            total=total,
            page=query.page,
            page_size=query.page_size
        )
    
    @classmethod
    async def get_all_permissions_service(
        cls,
        db: AsyncSession
    ) -> dict:
        """获取所有权限（用于分配）"""
        crud = PermissionCRUD(db)
        
        # 获取所有启用的权限
        conditions = [PermissionModel.status == 1]
        order_by = [PermissionModel.id.asc()]
        
        items, _ = await crud.get_list_crud(
            conditions=conditions,
            order_by=order_by,
            skip=0,
            limit=1000
        )
        
        # 转换为输出格式
        permission_list = [
            PermissionOutSchema.model_validate(item).model_dump()
            for item in items
        ]
        
        return success_response(data=permission_list, message="查询成功")
    
    @classmethod
    async def create_permission_service(
        cls,
        data: PermissionCreateSchema,
        current_user_id: int,
        db: AsyncSession
    ) -> PermissionOutSchema:
        """创建权限"""
        crud = PermissionCRUD(db)
        
        # 检查权限编码是否存在
        if await crud.check_code_exists_crud(data.permission_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="权限编码已存在"
            )
        
        # 准备数据
        permission_data = data.model_dump()
        permission_data['created_by'] = current_user_id
        permission_data['updated_by'] = current_user_id
        
        # 创建权限
        permission = await crud.create_crud(permission_data)
        
        return await cls.get_permission_detail_service(permission.id, db)
    
    @classmethod
    async def update_permission_service(
        cls,
        permission_id: int,
        data: PermissionUpdateSchema,
        current_user_id: int,
        db: AsyncSession
    ) -> PermissionOutSchema:
        """更新权限"""
        crud = PermissionCRUD(db)
        
        # 检查权限是否存在
        permission = await crud.get_by_id_crud(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="权限不存在"
            )
        
        # 检查权限编码是否重复
        if data.permission_code and await crud.check_code_exists_crud(data.permission_code, permission_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="权限编码已存在"
            )
        
        # 准备更新数据
        update_data = data.model_dump(exclude_unset=True)
        update_data['updated_by'] = current_user_id
        
        # 更新权限
        await crud.update_crud(permission_id, update_data)
        
        return await cls.get_permission_detail_service(permission_id, db)
    
    @classmethod
    async def delete_permission_service(
        cls,
        permission_ids: List[int],
        db: AsyncSession
    ) -> None:
        """删除权限"""
        crud = PermissionCRUD(db)
        
        # 删除权限
        await crud.delete_crud(permission_ids)
