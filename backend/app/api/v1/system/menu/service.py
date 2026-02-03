"""
菜单业务逻辑层
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.v1.system.menu.crud import MenuCRUD
from app.api.v1.system.menu.schema import (
    MenuCreateSchema,
    MenuUpdateSchema,
    MenuOutSchema,
    MenuTreeSchema,
    MenuRouteSchema
)
from app.api.v1.system.menu.model import MenuModel
from app.common.response import success_response


class MenuService:
    """菜单服务"""
    
    @classmethod
    async def get_menu_detail_service(
        cls,
        menu_id: int,
        db: AsyncSession
    ) -> MenuOutSchema:
        """
        获取菜单详情
        
        Args:
            menu_id: 菜单ID
            db: 数据库会话
            
        Returns:
            菜单详情
        """
        crud = MenuCRUD(db)
        menu = await crud.get_by_id_crud(menu_id)
        
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜单不存在"
            )
        
        return MenuOutSchema.model_validate(menu)
    
    @classmethod
    async def get_menu_list_service(
        cls,
        db: AsyncSession
    ) -> dict:
        """
        获取菜单列表（扁平列表）
        
        Args:
            db: 数据库会话
            
        Returns:
            菜单列表
        """
        crud = MenuCRUD(db)
        menus = await crud.get_all_menus_crud()
        
        menu_list = [MenuOutSchema.model_validate(menu).model_dump() for menu in menus]
        
        return success_response(data=menu_list, message="查询成功")
    
    @classmethod
    async def get_menu_tree_service(
        cls,
        db: AsyncSession
    ) -> dict:
        """
        获取菜单树形结构
        
        Args:
            db: 数据库会话
            
        Returns:
            菜单树
        """
        crud = MenuCRUD(db)
        all_menus = await crud.get_all_menus_crud()
        
        tree = cls._build_menu_tree(all_menus, 0)
        
        return success_response(data=tree, message="查询成功")
    
    @classmethod
    def _build_menu_tree(
        cls,
        menus: List[MenuModel],
        parent_id: int
    ) -> List[dict]:
        """
        递归构建菜单树
        
        Args:
            menus: 所有菜单列表
            parent_id: 父菜单ID
            
        Returns:
            树形结构列表
        """
        tree = []
        
        for menu in menus:
            if menu.parent_id == parent_id:
                menu_data = MenuOutSchema.model_validate(menu)
                menu_dict = menu_data.model_dump()
                
                # 递归获取子菜单
                children = cls._build_menu_tree(menus, menu.id)
                if children:
                    menu_dict['children'] = children
                
                tree.append(menu_dict)
        
        return tree
    
    @classmethod
    async def get_menu_routes_service(
        cls,
        menu_ids: Optional[List[int]],
        db: AsyncSession
    ) -> dict:
        """
        获取前端路由（用于用户菜单）
        
        Args:
            menu_ids: 菜单ID列表（None表示获取所有）
            db: 数据库会话
            
        Returns:
            路由列表
        """
        crud = MenuCRUD(db)
        
        # 获取菜单列表
        if menu_ids:
            menus = await crud.get_menus_by_ids_crud(menu_ids)
        else:
            menus = await crud.get_all_menus_crud()
        
        # 只保留目录和菜单，排除按钮
        menus = [m for m in menus if m.menu_type in [1, 2] and m.status == 1]
        
        # 构建路由树
        routes = cls._build_menu_routes(menus, 0)
        
        return success_response(data=routes, message="查询成功")
    
    @classmethod
    def _build_menu_routes(
        cls,
        menus: List[MenuModel],
        parent_id: int
    ) -> List[dict]:
        """
        递归构建前端路由
        
        Args:
            menus: 菜单列表
            parent_id: 父菜单ID
            
        Returns:
            路由列表
        """
        routes = []
        
        for menu in menus:
            if menu.parent_id == parent_id:
                route = {
                    "path": menu.path or "",
                    "name": menu.menu_name,
                    "component": menu.component,
                    "redirect": menu.redirect,
                    "meta": {
                        "title": menu.menu_name,
                        "icon": menu.icon,
                        "isLink": bool(menu.is_link),
                        "isIframe": bool(menu.is_iframe),
                        "isCache": bool(menu.is_cache),
                        "isAffix": bool(menu.is_affix),
                        "isHide": not bool(menu.visible),
                    }
                }
                
                # 递归获取子路由
                children = cls._build_menu_routes(menus, menu.id)
                if children:
                    route['children'] = children
                
                routes.append(route)
        
        return routes
    
    @classmethod
    async def create_menu_service(
        cls,
        data: MenuCreateSchema,
        current_user_id: int,
        db: AsyncSession
    ) -> MenuOutSchema:
        """
        创建菜单
        
        Args:
            data: 菜单数据
            current_user_id: 当前用户ID
            db: 数据库会话
            
        Returns:
            新创建的菜单
        """
        crud = MenuCRUD(db)
        
        # 检查菜单名称是否存在
        if await crud.check_name_exists_crud(data.menu_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="菜单名称已存在"
            )
        
        # 检查权限标识是否存在（如果有）
        if data.perms and await crud.check_perms_exists_crud(data.perms):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="权限标识已存在"
            )
        
        # 检查父菜单是否存在
        if data.parent_id != 0:
            parent_menu = await crud.get_by_id_crud(data.parent_id)
            if not parent_menu:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="父菜单不存在"
                )
            
            # 按钮只能挂在菜单下
            if data.menu_type == 3 and parent_menu.menu_type != 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="按钮只能添加在菜单下"
                )
        
        # 准备数据
        menu_data = data.model_dump()
        menu_data['created_by'] = current_user_id
        menu_data['updated_by'] = current_user_id
        
        # 创建菜单
        menu = await crud.create_crud(menu_data)
        
        return await cls.get_menu_detail_service(menu.id, db)
    
    @classmethod
    async def update_menu_service(
        cls,
        menu_id: int,
        data: MenuUpdateSchema,
        current_user_id: int,
        db: AsyncSession
    ) -> MenuOutSchema:
        """
        更新菜单
        
        Args:
            menu_id: 菜单ID
            data: 更新数据
            current_user_id: 当前用户ID
            db: 数据库会话
            
        Returns:
            更新后的菜单
        """
        crud = MenuCRUD(db)
        
        # 检查菜单是否存在
        menu = await crud.get_by_id_crud(menu_id)
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜单不存在"
            )
        
        # 检查菜单名称是否重复
        if data.menu_name and await crud.check_name_exists_crud(data.menu_name, menu_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="菜单名称已存在"
            )
        
        # 检查权限标识是否重复
        if data.perms and await crud.check_perms_exists_crud(data.perms, menu_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="权限标识已存在"
            )
        
        # 检查父菜单
        if data.parent_id is not None:
            # 不能将菜单设置为自己的子菜单
            if data.parent_id == menu_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能将菜单设置为自己的子菜单"
                )
            
            # 检查父菜单是否存在
            if data.parent_id != 0:
                parent_menu = await crud.get_by_id_crud(data.parent_id)
                if not parent_menu:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="父菜单不存在"
                    )
                
                # 不能将菜单设置为自己的子孙菜单
                all_children = await crud.get_all_children_crud(menu_id)
                child_ids = [child.id for child in all_children]
                if data.parent_id in child_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="不能将菜单设置为自己的子孙菜单"
                    )
        
        # 准备更新数据
        update_data = data.model_dump(exclude_unset=True)
        update_data['updated_by'] = current_user_id
        
        # 更新菜单
        await crud.update_crud(menu_id, update_data)
        
        return await cls.get_menu_detail_service(menu_id, db)
    
    @classmethod
    async def delete_menu_service(
        cls,
        menu_ids: List[int],
        db: AsyncSession
    ) -> None:
        """
        删除菜单
        
        Args:
            menu_ids: 菜单ID列表
            db: 数据库会话
        """
        crud = MenuCRUD(db)
        
        for menu_id in menu_ids:
            # 检查菜单是否存在
            menu = await crud.get_by_id_crud(menu_id)
            if not menu:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"菜单ID {menu_id} 不存在"
                )
            
            # 检查是否有子菜单
            if await crud.has_children_crud(menu_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"菜单【{menu.menu_name}】存在子菜单，不能删除"
                )
        
        # 先删除角色-菜单关联
        from sqlalchemy import text
        for menu_id in menu_ids:
            await db.execute(text(f"DELETE FROM sys_role_menu WHERE menu_id = {menu_id}"))
        
        # 删除菜单（硬删除）
        await crud.delete_crud(menu_ids)
