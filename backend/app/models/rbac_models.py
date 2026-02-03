# -*- coding: utf-8 -*-
# @author: rebort
"""
标准 RBAC 权限模型
"""
import typing
from sqlalchemy import Column, String, Integer, BigInteger, SmallInteger, select, and_
from sqlalchemy.orm import aliased

from app.models.base import Base


class Permission(Base):
    """权限表"""
    __tablename__ = 'permission'

    permission_code = Column(String(100), nullable=False, unique=True, index=True, comment='权限编码')
    permission_name = Column(String(100), nullable=False, comment='权限名称')
    permission_type = Column(SmallInteger, nullable=False, comment='1菜单权限 2按钮权限 3数据权限 4API权限')
    resource_type = Column(String(50), nullable=True, comment='资源类型')
    resource_id = Column(BigInteger, nullable=True, comment='关联资源ID')
    status = Column(SmallInteger, nullable=True, default=1, comment='1启用 0禁用')
    sort = Column(Integer, nullable=True, default=0, comment='排序')
    description = Column(String(500), nullable=True, comment='描述')

    @classmethod
    async def get_by_code(cls, code: str):
        """根据权限编码获取权限"""
        stmt = select(*cls.get_table_columns()).where(
            cls.permission_code == code,
            cls.enabled_flag == 1
        )
        return await cls.get_result(stmt, first=True)

    @classmethod
    async def get_by_codes(cls, codes: typing.List[str]):
        """根据权限编码列表获取权限"""
        stmt = select(*cls.get_table_columns()).where(
            cls.permission_code.in_(codes),
            cls.enabled_flag == 1
        ).order_by(cls.sort)
        return await cls.get_result(stmt)

    @classmethod
    async def get_by_type(cls, permission_type: int):
        """根据权限类型获取权限列表"""
        stmt = select(*cls.get_table_columns()).where(
            cls.permission_type == permission_type,
            cls.enabled_flag == 1,
            cls.status == 1
        ).order_by(cls.sort)
        return await cls.get_result(stmt)

    @classmethod
    async def get_all_permissions(cls):
        """获取所有启用的权限"""
        stmt = select(*cls.get_table_columns()).where(
            cls.enabled_flag == 1,
            cls.status == 1
        ).order_by(cls.permission_type, cls.sort)
        return await cls.get_result(stmt)


class UserRole(Base):
    """用户-角色关联表"""
    __tablename__ = 'user_role'

    user_id = Column(BigInteger, nullable=False, index=True, comment='用户ID')
    role_id = Column(BigInteger, nullable=False, index=True, comment='角色ID')

    @classmethod
    async def get_roles_by_user_id(cls, user_id: int):
        """获取用户的所有角色ID"""
        stmt = select(cls.role_id).where(
            cls.user_id == user_id,
            cls.enabled_flag == 1
        )
        result = await cls.get_result(stmt)
        return [row['role_id'] for row in result] if result else []

    @classmethod
    async def get_users_by_role_id(cls, role_id: int):
        """获取角色下的所有用户ID"""
        stmt = select(cls.user_id).where(
            cls.role_id == role_id,
            cls.enabled_flag == 1
        )
        result = await cls.get_result(stmt)
        return [row['user_id'] for row in result] if result else []

    @classmethod
    async def batch_create(cls, user_id: int, role_ids: typing.List[int], created_by: int = None):
        """批量创建用户角色关联"""
        # 先删除旧的关联
        await cls.delete_by_user_id(user_id)
        
        # 创建新的关联
        for role_id in role_ids:
            await cls.create_or_update({
                'user_id': user_id,
                'role_id': role_id,
                'created_by': created_by
            })
        return True

    @classmethod
    async def delete_by_user_id(cls, user_id: int):
        """删除用户的所有角色关联（硬删除）"""
        from sqlalchemy import delete as sql_delete
        stmt = sql_delete(cls).where(cls.user_id == user_id)
        result = await cls.execute(stmt)
        return result.rowcount if result else 0

    @classmethod
    async def delete_by_role_id(cls, role_id: int):
        """删除角色的所有用户关联（硬删除）"""
        from sqlalchemy import delete as sql_delete
        stmt = sql_delete(cls).where(cls.role_id == role_id)
        result = await cls.execute(stmt)
        return result.rowcount if result else 0


class RoleMenu(Base):
    """角色-菜单关联表"""
    __tablename__ = 'role_menu'

    role_id = Column(BigInteger, nullable=False, index=True, comment='角色ID')
    menu_id = Column(BigInteger, nullable=False, index=True, comment='菜单ID')

    @classmethod
    async def get_menus_by_role_id(cls, role_id: int):
        """获取角色的所有菜单ID"""
        stmt = select(cls.menu_id).where(
            cls.role_id == role_id,
            cls.enabled_flag == 1
        )
        result = await cls.get_result(stmt)
        return [row['menu_id'] for row in result] if result else []

    @classmethod
    async def get_menus_by_role_ids(cls, role_ids: typing.List[int]):
        """获取多个角色的所有菜单ID（去重）"""
        stmt = select(cls.menu_id).where(
            cls.role_id.in_(role_ids),
            cls.enabled_flag == 1
        ).distinct()
        result = await cls.get_result(stmt)
        return [row['menu_id'] for row in result] if result else []

    @classmethod
    async def batch_create(cls, role_id: int, menu_ids: typing.List[int], created_by: int = None):
        """批量创建角色菜单关联"""
        # 先删除旧的关联
        await cls.delete_by_role_id(role_id)
        
        # 创建新的关联
        for menu_id in menu_ids:
            await cls.create_or_update({
                'role_id': role_id,
                'menu_id': menu_id,
                'created_by': created_by
            })
        return True

    @classmethod
    async def delete_by_role_id(cls, role_id: int):
        """删除角色的所有菜单关联（硬删除）"""
        from sqlalchemy import delete as sql_delete
        stmt = sql_delete(cls).where(cls.role_id == role_id)
        result = await cls.execute(stmt)
        return result.rowcount if result else 0

    @classmethod
    async def delete_by_menu_id(cls, menu_id: int):
        """删除菜单的所有角色关联（硬删除）"""
        from sqlalchemy import delete as sql_delete
        stmt = sql_delete(cls).where(cls.menu_id == menu_id)
        result = await cls.execute(stmt)
        return result.rowcount if result else 0


class RolePermission(Base):
    """角色-权限关联表"""
    __tablename__ = 'role_permission'

    role_id = Column(BigInteger, nullable=False, index=True, comment='角色ID')
    permission_id = Column(BigInteger, nullable=False, index=True, comment='权限ID')

    @classmethod
    async def get_permissions_by_role_id(cls, role_id: int):
        """获取角色的所有权限ID"""
        stmt = select(cls.permission_id).where(
            cls.role_id == role_id,
            cls.enabled_flag == 1
        )
        result = await cls.get_result(stmt)
        return [row['permission_id'] for row in result] if result else []

    @classmethod
    async def get_permissions_by_role_ids(cls, role_ids: typing.List[int]):
        """获取多个角色的所有权限ID（去重）"""
        stmt = select(cls.permission_id).where(
            cls.role_id.in_(role_ids),
            cls.enabled_flag == 1
        ).distinct()
        result = await cls.get_result(stmt)
        return [row['permission_id'] for row in result] if result else []

    @classmethod
    async def batch_create(cls, role_id: int, permission_ids: typing.List[int], created_by: int = None):
        """批量创建角色权限关联"""
        # 先删除旧的关联
        await cls.delete_by_role_id(role_id)
        
        # 创建新的关联
        for permission_id in permission_ids:
            await cls.create_or_update({
                'role_id': role_id,
                'permission_id': permission_id,
                'created_by': created_by
            })
        return True

    @classmethod
    async def delete_by_role_id(cls, role_id: int):
        """删除角色的所有权限关联（硬删除）"""
        from sqlalchemy import delete as sql_delete
        stmt = sql_delete(cls).where(cls.role_id == role_id)
        result = await cls.execute(stmt)
        return result.rowcount if result else 0

    @classmethod
    async def delete_by_permission_id(cls, permission_id: int):
        """删除权限的所有角色关联（硬删除）"""
        from sqlalchemy import delete as sql_delete
        stmt = sql_delete(cls).where(cls.permission_id == permission_id)
        result = await cls.execute(stmt)
        return result.rowcount if result else 0
