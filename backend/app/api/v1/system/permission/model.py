"""
权限数据模型
"""

from sqlalchemy import Column, String, Integer, Text
from app.core.base_model import BaseModel


class PermissionModel(BaseModel):
    """权限模型"""
    
    __tablename__ = "sys_permission"
    __table_args__ = {'comment': '权限表'}
    
    permission_name = Column(String(100), nullable=False, comment="权限名称")
    permission_code = Column(String(100), nullable=False, unique=True, index=True, comment="权限编码")
    permission_type = Column(Integer, nullable=False, comment="权限类型（1:菜单 2:按钮 3:接口 4:数据）")
    
    resource_type = Column(String(50), nullable=True, comment="资源类型")
    resource_id = Column(Integer, nullable=True, comment="关联资源ID")
    
    description = Column(String(500), nullable=True, comment="权限描述")
    status = Column(Integer, nullable=True, default=1, comment="状态（0:禁用 1:启用）")
