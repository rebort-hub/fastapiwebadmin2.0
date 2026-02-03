"""
角色数据模型
"""

from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base_model import BaseModel

# 角色-菜单关联表
role_menu = Table(
    'sys_role_menu',
    BaseModel.metadata,
    Column('role_id', Integer, ForeignKey('sys_role.id', ondelete='CASCADE'), primary_key=True),
    Column('menu_id', Integer, ForeignKey('sys_menu.id', ondelete='CASCADE'), primary_key=True),
)

# 角色-部门关联表（自定义数据权限）
role_dept = Table(
    'sys_role_dept',
    BaseModel.metadata,
    Column('role_id', Integer, ForeignKey('sys_role.id', ondelete='CASCADE'), primary_key=True),
    Column('dept_id', Integer, ForeignKey('sys_dept.id', ondelete='CASCADE'), primary_key=True),
)

# 用户-角色关联表（导入避免重复定义）
from app.api.v1.system.user.model import user_role


class RoleModel(BaseModel):
    """角色模型"""
    
    __tablename__ = "sys_role"
    __table_args__ = {'comment': '角色表'}
    
    role_name = Column(String(50), nullable=False, unique=True, comment="角色名称")
    role_key = Column(String(50), nullable=False, unique=True, comment="角色权限字符串")
    role_sort = Column(Integer, default=0, comment="显示顺序")
    data_scope = Column(Integer, default=1, comment="数据范围（1:仅本人 2:本部门 3:本部门及以下 4:全部 5:自定义）")
    status = Column(Integer, default=1, comment="角色状态（0:停用 1:正常）")
    remark = Column(Text, nullable=True, comment="备注")
    
    # 关联关系
    menus = relationship(
        "MenuModel",
        secondary=role_menu,
        back_populates="roles",
        lazy="selectin"
    )
    
    depts = relationship(
        "DeptModel",
        secondary=role_dept,
        back_populates="roles",
        lazy="selectin"
    )
    
    users = relationship(
        "UserModel",
        secondary=user_role,
        back_populates="roles",
        lazy="selectin"
    )
