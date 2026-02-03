"""
用户数据模型
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base_model import BaseModel

# 用户-角色关联表
user_role = Table(
    'sys_user_role',
    BaseModel.metadata,
    Column('user_id', Integer, ForeignKey('sys_user.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('sys_role.id', ondelete='CASCADE'), primary_key=True),
)


class UserModel(BaseModel):
    """用户模型"""
    
    __tablename__ = "sys_user"
    __table_args__ = {'comment': '用户表'}
    
    username = Column(String(64), nullable=False, unique=True, index=True, comment="用户名")
    password = Column(Text, nullable=False, comment="密码（加密）")
    nickname = Column(String(255), nullable=False, comment="用户昵称")
    email = Column(String(64), nullable=True, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="手机号")
    avatar = Column(Text, nullable=True, comment="头像URL")
    
    user_type = Column(Integer, nullable=False, default=0, comment="用户类型（0:普通用户 10:超级管理员）")
    status = Column(Integer, nullable=False, default=1, comment="用户状态（0:禁用 1:启用）")
    gender = Column(Integer, nullable=True, default=0, comment="性别（0:未知 1:男 2:女）")
    
    dept_id = Column(Integer, ForeignKey('sys_dept.id'), nullable=True, comment="部门ID")
    post = Column(String(100), nullable=True, comment="岗位")
    remark = Column(String(500), nullable=True, comment="备注")
    tags = Column(JSON, nullable=True, comment="个性标签（JSON数组）")
    
    last_login_time = Column(DateTime, nullable=True, comment="最后登录时间")
    last_login_ip = Column(String(50), nullable=True, comment="最后登录IP")
    
    # 关联关系
    roles = relationship(
        "RoleModel",
        secondary=user_role,
        back_populates="users",
        lazy="selectin"
    )
    
    dept = relationship(
        "DeptModel",
        foreign_keys=[dept_id],
        lazy="selectin"
    )
