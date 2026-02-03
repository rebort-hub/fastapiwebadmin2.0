"""
部门业务逻辑层
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.v1.system.dept.crud import DeptCRUD
from app.api.v1.system.dept.schema import (
    DeptCreateSchema,
    DeptUpdateSchema,
    DeptOutSchema,
    DeptTreeSchema
)
from app.api.v1.system.dept.model import DeptModel
from app.common.response import success_response


class DeptService:
    """部门服务"""
    
    @classmethod
    async def get_dept_detail_service(
        cls,
        dept_id: int,
        db: AsyncSession
    ) -> DeptOutSchema:
        """
        获取部门详情
        
        Args:
            dept_id: 部门ID
            db: 数据库会话
            
        Returns:
            部门详情
        """
        crud = DeptCRUD(db)
        dept = await crud.get_by_id_crud(dept_id)
        
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="部门不存在"
            )
        
        # 构建输出数据
        dept_data = DeptOutSchema.model_validate(dept)
        dept_data.leader_name = dept.leader.nickname if dept.leader else None
        
        return dept_data
    
    @classmethod
    async def get_dept_list_service(
        cls,
        db: AsyncSession
    ) -> dict:
        """
        获取部门列表（扁平列表）
        
        Args:
            db: 数据库会话
            
        Returns:
            部门列表
        """
        crud = DeptCRUD(db)
        
        # 获取所有部门
        depts = await crud.get_all_depts_crud()
        
        # 转换为输出格式
        dept_list = []
        for dept in depts:
            dept_data = DeptOutSchema.model_validate(dept)
            dept_data.leader_name = dept.leader.nickname if dept.leader else None
            dept_list.append(dept_data.model_dump())
        
        return success_response(data=dept_list, message="查询成功")
    
    @classmethod
    async def get_dept_tree_service(
        cls,
        db: AsyncSession
    ) -> dict:
        """
        获取部门树形结构
        
        Args:
            db: 数据库会话
            
        Returns:
            部门树
        """
        crud = DeptCRUD(db)
        
        # 获取所有部门
        all_depts = await crud.get_all_depts_crud()
        
        # 构建树形结构
        tree = cls._build_dept_tree(all_depts, 0)
        
        return success_response(data=tree, message="查询成功")
    
    @classmethod
    def _build_dept_tree(
        cls,
        depts: List[DeptModel],
        parent_id: int
    ) -> List[dict]:
        """
        递归构建部门树
        
        Args:
            depts: 所有部门列表
            parent_id: 父部门ID
            
        Returns:
            树形结构列表
        """
        tree = []
        
        for dept in depts:
            if dept.parent_id == parent_id:
                dept_data = DeptOutSchema.model_validate(dept)
                dept_data.leader_name = dept.leader.nickname if dept.leader else None
                dept_dict = dept_data.model_dump()
                
                # 递归获取子部门
                children = cls._build_dept_tree(depts, dept.id)
                if children:
                    dept_dict['children'] = children
                
                tree.append(dept_dict)
        
        return tree
    
    @classmethod
    async def create_dept_service(
        cls,
        data: DeptCreateSchema,
        current_user_id: int,
        db: AsyncSession
    ) -> DeptOutSchema:
        """
        创建部门
        
        Args:
            data: 部门数据
            current_user_id: 当前用户ID
            db: 数据库会话
            
        Returns:
            新创建的部门
        """
        crud = DeptCRUD(db)
        
        # 检查部门名称是否存在
        if await crud.check_name_exists_crud(data.dept_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部门名称已存在"
            )
        
        # 检查部门编码是否存在
        if data.dept_code and await crud.check_code_exists_crud(data.dept_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部门编码已存在"
            )
        
        # 检查父部门是否存在
        if data.parent_id != 0:
            parent_dept = await crud.get_by_id_crud(data.parent_id)
            if not parent_dept:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="父部门不存在"
                )
        
        # 准备数据
        dept_data = data.model_dump()
        dept_data['created_by'] = current_user_id
        dept_data['updated_by'] = current_user_id
        
        # 生成祖级列表
        dept_data['ancestors'] = await cls._generate_ancestors(data.parent_id, crud)
        
        # 创建部门
        dept = await crud.create_crud(dept_data)
        
        return await cls.get_dept_detail_service(dept.id, db)
    
    @classmethod
    async def update_dept_service(
        cls,
        dept_id: int,
        data: DeptUpdateSchema,
        current_user_id: int,
        db: AsyncSession
    ) -> DeptOutSchema:
        """
        更新部门
        
        Args:
            dept_id: 部门ID
            data: 更新数据
            current_user_id: 当前用户ID
            db: 数据库会话
            
        Returns:
            更新后的部门
        """
        crud = DeptCRUD(db)
        
        # 检查部门是否存在
        dept = await crud.get_by_id_crud(dept_id)
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="部门不存在"
            )
        
        # 检查部门名称是否重复
        if data.dept_name and await crud.check_name_exists_crud(data.dept_name, dept_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部门名称已存在"
            )
        
        # 检查部门编码是否重复
        if data.dept_code and await crud.check_code_exists_crud(data.dept_code, dept_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部门编码已存在"
            )
        
        # 检查父部门
        if data.parent_id is not None:
            # 不能将部门设置为自己的子部门
            if data.parent_id == dept_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能将部门设置为自己的子部门"
                )
            
            # 检查父部门是否存在
            if data.parent_id != 0:
                parent_dept = await crud.get_by_id_crud(data.parent_id)
                if not parent_dept:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="父部门不存在"
                    )
                
                # 不能将部门设置为自己的子孙部门
                all_children = await crud.get_all_children_crud(dept_id)
                child_ids = [child.id for child in all_children]
                if data.parent_id in child_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="不能将部门设置为自己的子孙部门"
                    )
        
        # 准备更新数据
        update_data = data.model_dump(exclude_unset=True)
        update_data['updated_by'] = current_user_id
        
        # 如果修改了父部门，需要更新祖级列表
        if data.parent_id is not None and data.parent_id != dept.parent_id:
            update_data['ancestors'] = await cls._generate_ancestors(data.parent_id, crud)
        
        # 更新部门
        await crud.update_crud(dept_id, update_data)
        
        # 如果修改了父部门，需要更新所有子部门的祖级列表
        if data.parent_id is not None and data.parent_id != dept.parent_id:
            await cls._update_children_ancestors(dept_id, crud)
        
        return await cls.get_dept_detail_service(dept_id, db)
    
    @classmethod
    async def delete_dept_service(
        cls,
        dept_ids: List[int],
        db: AsyncSession
    ) -> None:
        """
        删除部门
        
        Args:
            dept_ids: 部门ID列表
            db: 数据库会话
        """
        crud = DeptCRUD(db)
        
        for dept_id in dept_ids:
            # 检查部门是否存在
            dept = await crud.get_by_id_crud(dept_id)
            if not dept:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"部门ID {dept_id} 不存在"
                )
            
            # 检查是否有子部门
            if await crud.has_children_crud(dept_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"部门【{dept.dept_name}】存在子部门，不能删除"
                )
            
            # 检查是否有用户
            user_count = await crud.get_user_count_crud(dept_id)
            if user_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"部门【{dept.dept_name}】下有 {user_count} 个用户，不能删除"
                )
        
        # 删除部门（硬删除）
        await crud.delete_crud(dept_ids)
    
    @classmethod
    async def _generate_ancestors(
        cls,
        parent_id: int,
        crud: DeptCRUD
    ) -> str:
        """
        生成祖级列表
        
        Args:
            parent_id: 父部门ID
            crud: CRUD实例
            
        Returns:
            祖级列表字符串（逗号分隔）
        """
        if parent_id == 0:
            return "0"
        
        ancestors = []
        current_id = parent_id
        
        # 向上遍历获取所有祖先
        while current_id != 0:
            dept = await crud.get_by_id_crud(current_id)
            if not dept:
                break
            ancestors.insert(0, str(current_id))
            current_id = dept.parent_id
        
        ancestors.insert(0, "0")
        return ",".join(ancestors)
    
    @classmethod
    async def _update_children_ancestors(
        cls,
        dept_id: int,
        crud: DeptCRUD
    ) -> None:
        """
        更新所有子部门的祖级列表
        
        Args:
            dept_id: 部门ID
            crud: CRUD实例
        """
        # 获取所有子部门
        all_children = await crud.get_all_children_crud(dept_id)
        
        # 更新每个子部门的祖级列表
        for child in all_children:
            ancestors = await cls._generate_ancestors(child.parent_id, crud)
            await crud.update_crud(child.id, {"ancestors": ancestors})
