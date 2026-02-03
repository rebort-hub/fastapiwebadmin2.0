"""
部门数据模型
"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base_model import BaseModel
# 导入关联表（避免重复定义）
from app.api.v1.system.role.model import role_dept


class DeptModel(BaseModel):
    """部门模型"""
    
    __tablename__ = "sys_dept"
    __table_args__ = {'comment': '部门表'}
    
    dept_name = Column(String(100), nullable=False, comment="部门名称")
    dept_code = Column(String(64), nullable=True, unique=True, index=True, comment="部门编码")
    parent_id = Column(Integer, nullable=True, default=0, comment="父部门ID（0表示顶级部门）")
    ancestors = Column(String(500), nullable=True, comment="祖级列表（逗号分隔）")
    
    leader_id = Column(Integer, ForeignKey('sys_user.id'), nullable=True, comment="负责人ID")
    phone = Column(String(20), nullable=True, comment="联系电话")
    email = Column(String(100), nullable=True, comment="邮箱")
    
    sort = Column(Integer, nullable=True, default=0, comment="排序")
    status = Column(Integer, nullable=True, default=1, comment="状态（0:禁用 1:启用）")
    description = Column(String(500), nullable=True, comment="部门描述")
    
    # 关联关系
    roles = relationship(
        "RoleModel",
        secondary=role_dept,
        back_populates="depts",
        lazy="selectin"
    )
    
    leader = relationship(
        "UserModel",
        foreign_keys=[leader_id],
        lazy="selectin"
    )
