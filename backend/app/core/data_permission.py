"""
数据权限过滤器
"""

from typing import Any, Optional, List, Set
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.api.v1.system.user.model import UserModel
from app.api.v1.system.dept.model import DeptModel


class DataPermission:
    """数据权限过滤器"""
    
    # 数据权限常量
    DATA_SCOPE_SELF = 1  # 仅本人数据
    DATA_SCOPE_DEPT = 2  # 本部门数据
    DATA_SCOPE_DEPT_AND_CHILD = 3  # 本部门及以下数据
    DATA_SCOPE_ALL = 4  # 全部数据
    DATA_SCOPE_CUSTOM = 5  # 自定义数据
    
    def __init__(self, model: Any, db: AsyncSession, current_user: UserModel):
        """
        初始化数据权限过滤器
        
        Args:
            model: 数据模型类
            db: 数据库会话
            current_user: 当前用户对象
        """
        self.model = model
        self.db = db
        self.current_user = current_user
        self._dept_cache = {}  # 部门缓存
    
    async def apply_data_permission(self, stmt: Any) -> Any:
        """
        应用数据权限过滤
        
        Args:
            stmt: SQLAlchemy查询语句
            
        Returns:
            应用权限过滤后的查询语句
        """
        condition = await self._get_permission_condition()
        if condition is not None:
            stmt = stmt.where(condition)
        return stmt
    
    async def _get_permission_condition(self) -> Optional[Any]:
        """
        获取权限过滤条件
        
        Returns:
            SQLAlchemy过滤条件或None（None表示无限制）
        """
        # 超级管理员可以查看所有数据
        if self.current_user.user_type == 10:
            return None
        
        # 如果模型没有created_by字段，不进行数据权限过滤
        if not hasattr(self.model, "created_by"):
            return None
        
        # 获取用户的所有角色
        roles = getattr(self.current_user, "roles", []) or []
        if not roles:
            # 没有角色，只能查看自己创建的数据
            return self.model.created_by == self.current_user.id
        
        # 收集所有角色的数据权限范围
        data_scopes = set()
        custom_dept_ids = set()
        
        for role in roles:
            if hasattr(role, 'data_scope') and role.data_scope:
                data_scopes.add(role.data_scope)
                
                # 如果是自定义权限，收集自定义部门ID
                if role.data_scope == self.DATA_SCOPE_CUSTOM:
                    # 这里需要从角色-部门关联表获取自定义部门
                    custom_depts = await self._get_role_custom_depts(role.id)
                    custom_dept_ids.update(custom_depts)
        
        # 如果没有数据权限配置，默认只能查看自己的数据
        if not data_scopes:
            return self.model.created_by == self.current_user.id
        
        # 全部数据权限 - 无限制
        if self.DATA_SCOPE_ALL in data_scopes:
            return None
        
        # 构建权限条件列表
        conditions = []
        
        # 仅本人数据权限
        if self.DATA_SCOPE_SELF in data_scopes:
            conditions.append(self.model.created_by == self.current_user.id)
        
        # 本部门数据权限
        if self.DATA_SCOPE_DEPT in data_scopes and self.current_user.dept_id:
            dept_condition = await self._get_dept_condition([self.current_user.dept_id])
            if dept_condition is not None:
                conditions.append(dept_condition)
        
        # 本部门及以下数据权限
        if self.DATA_SCOPE_DEPT_AND_CHILD in data_scopes and self.current_user.dept_id:
            child_dept_ids = await self._get_child_dept_ids(self.current_user.dept_id)
            dept_condition = await self._get_dept_condition(child_dept_ids)
            if dept_condition is not None:
                conditions.append(dept_condition)
        
        # 自定义数据权限
        if self.DATA_SCOPE_CUSTOM in data_scopes and custom_dept_ids:
            dept_condition = await self._get_dept_condition(list(custom_dept_ids))
            if dept_condition is not None:
                conditions.append(dept_condition)
        
        # 如果没有任何条件，默认只能查看自己的数据
        if not conditions:
            return self.model.created_by == self.current_user.id
        
        # 多个条件取并集（OR）
        return or_(*conditions)
    
    async def _get_dept_condition(self, dept_ids: List[int]) -> Optional[Any]:
        """
        根据部门ID列表构建过滤条件
        
        Args:
            dept_ids: 部门ID列表
            
        Returns:
            过滤条件或None
        """
        if not dept_ids:
            return None
        
        # 方案1：如果模型有dept_id字段，直接过滤
        if hasattr(self.model, "dept_id"):
            return self.model.dept_id.in_(dept_ids)
        
        # 方案2：通过创建人的部门过滤
        if hasattr(self.model, "created_by"):
            # 子查询：获取指定部门的所有用户ID
            user_subquery = select(UserModel.id).where(
                UserModel.dept_id.in_(dept_ids),
                UserModel.status == 1
            )
            return self.model.created_by.in_(user_subquery)
        
        return None
    
    async def _get_child_dept_ids(self, dept_id: int) -> List[int]:
        """
        递归获取所有子部门ID（包括自身）
        
        Args:
            dept_id: 父部门ID
            
        Returns:
            部门ID列表
        """
        if dept_id in self._dept_cache:
            return self._dept_cache[dept_id]
        
        result = [dept_id]  # 包括自身
        
        try:
            # 查询直接子部门
            stmt = select(DeptModel.id).where(
                DeptModel.parent_id == dept_id,
                DeptModel.status == 1
            )
            children_result = await self.db.execute(stmt)
            children = children_result.scalars().all()
            
            # 递归查询子部门的子部门
            for child_id in children:
                child_dept_ids = await self._get_child_dept_ids(child_id)
                result.extend(child_dept_ids)
            
            # 去重
            result = list(set(result))
            
        except Exception as e:
            # 如果查询失败，只返回自身
            print(f"获取子部门失败: {e}")
            result = [dept_id]
        
        # 缓存结果
        self._dept_cache[dept_id] = result
        return result
    
    async def _get_role_custom_depts(self, role_id: int) -> List[int]:
        """
        获取角色的自定义部门ID列表
        
        Args:
            role_id: 角色ID
            
        Returns:
            部门ID列表
        """
        try:
            # 这里需要根据实际的角色-部门关联表来查询
            # 假设有sys_role_dept表存储角色和部门的关联关系
            from app.api.v1.system.role.model import RoleModel
            
            stmt = select(RoleModel).options(
                selectinload(RoleModel.depts)
            ).where(RoleModel.id == role_id)
            
            result = await self.db.execute(stmt)
            role = result.scalar_one_or_none()
            
            if role and hasattr(role, 'depts') and role.depts:
                return [dept.id for dept in role.depts]
            
        except Exception as e:
            print(f"获取角色自定义部门失败: {e}")
        
        return []


class DataPermissionMixin:
    """数据权限混入类，为CRUD类提供数据权限功能"""
    
    async def apply_data_permission(self, stmt: Any, current_user: UserModel) -> Any:
        """
        为查询语句应用数据权限
        
        Args:
            stmt: SQLAlchemy查询语句
            current_user: 当前用户
            
        Returns:
            应用权限后的查询语句
        """
        if not hasattr(self, 'db') or not hasattr(self, 'model'):
            return stmt
        
        permission = DataPermission(self.model, self.db, current_user)
        return await permission.apply_data_permission(stmt)
    
    async def get_list_with_permission(
        self, 
        current_user: UserModel,
        page: int = 1, 
        page_size: int = 10,
        **filters
    ) -> dict:
        """
        带权限的分页查询
        
        Args:
            current_user: 当前用户
            page: 页码
            page_size: 每页数量
            **filters: 其他过滤条件
            
        Returns:
            分页结果
        """
        # 构建基础查询
        stmt = select(self.model)
        
        # 应用过滤条件
        for key, value in filters.items():
            if value is not None and hasattr(self.model, key):
                stmt = stmt.where(getattr(self.model, key) == value)
        
        # 应用数据权限
        stmt = await self.apply_data_permission(stmt, current_user)
        
        # 计算总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()
        
        # 分页查询
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }


# 便捷函数
async def apply_data_permission(
    stmt: Any, 
    model: Any, 
    db: AsyncSession, 
    current_user: UserModel
) -> Any:
    """
    便捷函数：为查询语句应用数据权限
    
    Args:
        stmt: SQLAlchemy查询语句
        model: 数据模型类
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        应用权限后的查询语句
    """
    permission = DataPermission(model, db, current_user)
    return await permission.apply_data_permission(stmt)