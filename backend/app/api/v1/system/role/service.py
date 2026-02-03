"""
角色业务逻辑层
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.v1.system.role.crud import RoleCRUD
from app.api.v1.system.role.schema import (
    RoleCreateSchema,
    RoleUpdateSchema,
    RoleOutSchema,
    RoleQuerySchema
)
from app.api.v1.system.role.model import RoleModel
from app.common.response import page_response


class RoleService:
    """角色服务"""
    
    @classmethod
    async def get_role_detail_service(
        cls,
        role_id: int,
        db: AsyncSession
    ) -> RoleOutSchema:
        """
        获取角色详情
        
        Args:
            role_id: 角色ID
            db: 数据库会话
            
        Returns:
            角色详情
        """
        crud = RoleCRUD(db)
        role = await crud.get_by_id_crud(role_id)
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 构建输出数据
        role_data = RoleOutSchema.model_validate(role)
        role_data.menu_ids = [menu.id for menu in role.menus] if role.menus else []
        role_data.dept_ids = [dept.id for dept in role.depts] if role.depts else []
        
        return role_data
    
    @classmethod
    async def get_role_list_service(
        cls,
        query: RoleQuerySchema,
        db: AsyncSession
    ) -> dict:
        """
        获取角色列表
        
        Args:
            query: 查询参数
            db: 数据库会话
            
        Returns:
            分页数据
        """
        crud = RoleCRUD(db)
        
        # 构建查询条件
        conditions = []
        if query.role_name:
            conditions.append(RoleModel.role_name.like(f"%{query.role_name}%"))
        if query.role_key:
            conditions.append(RoleModel.role_key.like(f"%{query.role_key}%"))
        if query.status is not None:
            conditions.append(RoleModel.status == query.status)
        if query.begin_time:
            conditions.append(RoleModel.created_at >= query.begin_time)
        if query.end_time:
            conditions.append(RoleModel.created_at <= query.end_time)
        
        # 排序
        order_by = [RoleModel.role_sort.asc(), RoleModel.id.desc()]
        
        # 查询数据
        items, total = await crud.get_list_crud(
            conditions=conditions,
            order_by=order_by,
            skip=query.skip,
            limit=query.limit
        )
        
        # 转换为输出格式
        role_list = []
        for role in items:
            role_data = RoleOutSchema.model_validate(role)
            role_data.menu_ids = [menu.id for menu in role.menus] if role.menus else []
            role_data.dept_ids = [dept.id for dept in role.depts] if role.depts else []
            role_list.append(role_data.model_dump())
        
        return page_response(
            items=role_list,
            total=total,
            page=query.page,
            page_size=query.page_size
        )

    @classmethod
    async def create_role_service(
        cls,
        data: RoleCreateSchema,
        current_user_id: int,
        db: AsyncSession
    ) -> RoleOutSchema:
        """
        创建角色
        
        Args:
            data: 角色数据
            current_user_id: 当前用户ID
            db: 数据库会话
            
        Returns:
            新创建的角色
        """
        crud = RoleCRUD(db)
        
        # 检查角色名称是否存在
        if await crud.check_name_exists_crud(data.role_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色名称已存在"
            )
        
        # 检查角色权限字符串是否存在
        if await crud.check_key_exists_crud(data.role_key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色权限字符串已存在"
            )
        
        # 准备数据
        role_data = data.model_dump(exclude={'menu_ids', 'dept_ids'})
        role_data['created_by'] = current_user_id
        role_data['updated_by'] = current_user_id
        
        # 创建角色
        role = await crud.create_crud(role_data)
        
        # 关联菜单
        if data.menu_ids:
            from app.api.v1.system.menu.model import MenuModel
            from sqlalchemy import select
            stmt = select(MenuModel).where(MenuModel.id.in_(data.menu_ids))
            result = await db.execute(stmt)
            menus = result.scalars().all()
            role.menus = list(menus)
            await db.commit()
        
        # 关联部门（自定义权限）
        if data.data_scope == 5 and data.dept_ids:
            from app.api.v1.system.dept.model import DeptModel
            from sqlalchemy import select
            stmt = select(DeptModel).where(DeptModel.id.in_(data.dept_ids))
            result = await db.execute(stmt)
            depts = result.scalars().all()
            role.depts = list(depts)
            await db.commit()
        
        return await cls.get_role_detail_service(role.id, db)
    
    @classmethod
    async def update_role_service(
        cls,
        role_id: int,
        data: RoleUpdateSchema,
        current_user_id: int,
        db: AsyncSession
    ) -> RoleOutSchema:
        """
        更新角色
        
        Args:
            role_id: 角色ID
            data: 更新数据
            current_user_id: 当前用户ID
            db: 数据库会话
            
        Returns:
            更新后的角色
        """
        crud = RoleCRUD(db)
        
        # 检查角色是否存在
        role = await crud.get_by_id_crud(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 检查角色名称是否重复
        if data.role_name and await crud.check_name_exists_crud(data.role_name, role_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色名称已存在"
            )
        
        # 检查角色权限字符串是否重复
        if data.role_key and await crud.check_key_exists_crud(data.role_key, role_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色权限字符串已存在"
            )
        
        # 准备更新数据
        update_data = data.model_dump(exclude_unset=True, exclude={'menu_ids', 'dept_ids'})
        update_data['updated_by'] = current_user_id
        
        # 更新角色基本信息
        if update_data:
            await crud.update_crud(role_id, update_data)
        
        # 更新菜单关联
        if data.menu_ids is not None:
            # 刷新role对象，确保获取最新的关联数据
            await db.refresh(role, ['menus'])
            
            # 清空旧的菜单关联
            role.menus.clear()
            await db.flush()
            
            # 添加新的菜单关联
            if data.menu_ids:
                from app.api.v1.system.menu.model import MenuModel
                from sqlalchemy import select
                stmt = select(MenuModel).where(MenuModel.id.in_(data.menu_ids))
                result = await db.execute(stmt)
                menus = result.scalars().all()
                role.menus.extend(menus)
            
            await db.commit()
        
        # 更新部门关联（自定义权限）
        if data.dept_ids is not None:
            # 刷新role对象，确保获取最新的关联数据
            await db.refresh(role, ['depts'])
            
            # 清空旧的部门关联
            role.depts.clear()
            await db.flush()
            
            # 添加新的部门关联
            if data.dept_ids:
                from app.api.v1.system.dept.model import DeptModel
                from sqlalchemy import select
                stmt = select(DeptModel).where(DeptModel.id.in_(data.dept_ids))
                result = await db.execute(stmt)
                depts = result.scalars().all()
                role.depts.extend(depts)
            
            await db.commit()
        
        return await cls.get_role_detail_service(role_id, db)
    
    @classmethod
    async def delete_role_service(
        cls,
        role_ids: List[int],
        db: AsyncSession
    ) -> None:
        """
        删除角色
        
        Args:
            role_ids: 角色ID列表
            db: 数据库会话
        """
        crud = RoleCRUD(db)
        
        # 检查角色是否被用户使用
        for role_id in role_ids:
            user_count = await crud.get_user_count_crud(role_id)
            if user_count > 0:
                role = await crud.get_by_id_crud(role_id)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"角色【{role.role_name}】已分配给用户，不能删除"
                )
        
        # 删除角色（会自动删除关联表数据）
        await crud.delete_crud(role_ids)
