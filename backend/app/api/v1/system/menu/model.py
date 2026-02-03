"""
菜单数据模型
"""

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.core.base_model import BaseModel
# 导入关联表（避免重复定义）
from app.api.v1.system.role.model import role_menu


class MenuModel(BaseModel):
    """菜单模型"""
    
    __tablename__ = "sys_menu"
    __table_args__ = {'comment': '菜单表'}
    
    # 基本信息
    menu_name = Column(String(50), nullable=False, comment="菜单名称")
    menu_type = Column(String(1), nullable=False, comment="菜单类型（M:目录 C:菜单 F:按钮）")
    parent_id = Column(Integer, nullable=True, default=0, comment="父菜单ID（0表示顶级）")
    
    # 路由信息
    path = Column(String(200), nullable=True, comment="路由路径")
    component = Column(String(255), nullable=True, comment="组件路径")
    query = Column(String(255), nullable=True, comment="路由参数")
    
    # 权限信息
    perms = Column(String(100), nullable=True, comment="权限标识")
    
    # 显示信息
    icon = Column(String(100), nullable=True, comment="菜单图标")
    order_num = Column(Integer, nullable=True, default=0, comment="显示顺序")
    visible = Column(Integer, nullable=True, default=1, comment="菜单状态（0:隐藏 1:显示）")
    status = Column(Integer, nullable=True, default=1, comment="菜单状态（0:停用 1:正常）")
    
    # 前端配置
    is_frame = Column(Integer, nullable=True, default=1, comment="是否为外链（0:是 1:否）")
    is_cache = Column(Integer, nullable=True, default=0, comment="是否缓存（0:缓存 1:不缓存）")
    
    # 其他
    remark = Column(String(500), nullable=True, comment="备注")
    
    # 关联关系
    roles = relationship(
        "RoleModel",
        secondary=role_menu,
        back_populates="menus",
        lazy="selectin"
    )
