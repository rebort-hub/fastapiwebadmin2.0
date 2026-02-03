"""
数据权限过滤器
实现5种数据权限范围
"""

from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class Permission:
    """数据权限过滤器"""
    
    # 数据权限常量
    DATA_SCOPE_SELF = 1  # 仅本人数据
    DATA_SCOPE_DEPT = 2  # 本部门数据
    DATA_SCOPE_DEPT_AND_CHILD = 3  # 本部门及以下数据
    DATA_SCOPE_ALL = 4  # 全部数据
    DATA_SCOPE_CUSTOM = 5  # 自定义数据
    
    def __init__(self, model: Any, db: AsyncSession, current_user: Any):
        """
        初始化权限过滤器
        
        Args:
            model: 数据模型类
            db: 数据库会话
            current_user: 当前用户对象
        """
        self.model = model
        self.db = db
        self.current_user = current_user
    
    async def filter_query(self, query: Any) -> Any:
        """
        过滤查询
        
        Args:
            query: SQLAlchemy查询对象
            
        Returns:
            过滤后的查询对象
        """
        condition = await self._get_permission_condition()
        return query.where(condition) if condition is not None else query
    
    async def _get_permission_condition(self) -> Optional[Any]:
        """
        获取权限过滤条件
        
        Returns:
            SQLAlchemy过滤条件或None
        """
        # 如果模型没有created_by字段，不限制
        if not hasattr(self.model, "created_by"):
            return None
        
        # 超级管理员可以查看所有数据
        if hasattr(self.current_user, 'user_type') and self.current_user.user_type == 10:
            return None
        
        # 如果用户没有角色，只能查看自己的数据
        roles = getattr(self.current_user, "roles", []) or []
        if not roles:
            return self.model.created_by == self.current_user.id
        
        # 获取所有角色的权限范围
        data_scopes = set()
        custom_dept_ids = set()
        
        for role in roles:
            data_scopes.add(role.data_scope)
            # 收集自定义权限的部门ID
            if role.data_scope == self.DATA_SCOPE_CUSTOM and hasattr(role, "depts"):
                custom_dept_ids.update(dept.id for dept in role.depts)
        
        # 全部数据权限
        if self.DATA_SCOPE_ALL in data_scopes:
            return None
        
        # 收集可访问的部门ID
        accessible_dept_ids = set()
        user_dept_id = getattr(self.current_user, "dept_id", None)
        
        # 自定义数据权限
        if self.DATA_SCOPE_CUSTOM in data_scopes:
            accessible_dept_ids.update(custom_dept_ids)
        
        # 本部门数据权限
        if self.DATA_SCOPE_DEPT in data_scopes and user_dept_id:
            accessible_dept_ids.add(user_dept_id)
        
        # 本部门及以下数据权限
        if self.DATA_SCOPE_DEPT_AND_CHILD in data_scopes and user_dept_id:
            child_dept_ids = await self._get_child_dept_ids(user_dept_id)
            accessible_dept_ids.update(child_dept_ids)
        
        # 如果有部门权限，使用部门过滤
        if accessible_dept_ids:
            # 尝试使用关系过滤（性能更好）
            try:
                from app.models.rbac_models import User
                if hasattr(self.model, "creator"):
                    return self.model.creator.has(
                        User.dept_id.in_(list(accessible_dept_ids))
                    )
            except:
                pass
            # 降级方案：只能查看自己的数据
            return self.model.created_by == self.current_user.id
        
        # 仅本人数据权限
        if self.DATA_SCOPE_SELF in data_scopes:
            return self.model.created_by == self.current_user.id
        
        # 默认：只能查看自己的数据
        return self.model.created_by == self.current_user.id
    
    async def _get_child_dept_ids(self, dept_id: int) -> list[int]:
        """
        递归获取所有子部门ID
        
        Args:
            dept_id: 部门ID
            
        Returns:
            部门ID列表（包括自身）
        """
        try:
            from app.models.rbac_models import Dept
            
            result = [dept_id]
            stmt = select(Dept).where(Dept.parent_id == dept_id)
            children = await self.db.execute(stmt)
            for child in children.scalars():
                result.extend(await self._get_child_dept_ids(child.id))
            return result
        except:
            return [dept_id]
