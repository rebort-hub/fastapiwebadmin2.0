"""
菜单数据验证模型
"""

from typing import Optional, List
from pydantic import Field
from app.core.base_schema import BaseSchema, TimestampSchema


class MenuCreateSchema(BaseSchema):
    """菜单创建Schema"""
    
    menu_name: str = Field(..., min_length=1, max_length=50, description="菜单名称")
    menu_type: str = Field(..., description="菜单类型（M:目录 C:菜单 F:按钮）")
    parent_id: int = Field(0, ge=0, description="父菜单ID")
    
    path: Optional[str] = Field(None, max_length=200, description="路由路径")
    component: Optional[str] = Field(None, max_length=255, description="组件路径")
    query: Optional[str] = Field(None, max_length=255, description="路由参数")
    
    perms: Optional[str] = Field(None, max_length=100, description="权限标识")
    
    icon: Optional[str] = Field(None, max_length=100, description="菜单图标")
    order_num: int = Field(0, ge=0, description="排序")
    visible: int = Field(1, ge=0, le=1, description="是否可见")
    status: int = Field(1, ge=0, le=1, description="菜单状态")
    
    is_frame: int = Field(1, ge=0, le=1, description="是否为外链")
    is_cache: int = Field(0, ge=0, le=1, description="是否缓存")
    
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class MenuUpdateSchema(BaseSchema):
    """菜单更新Schema"""
    
    menu_name: Optional[str] = Field(None, min_length=1, max_length=50, description="菜单名称")
    menu_type: Optional[str] = Field(None, description="菜单类型（M:目录 C:菜单 F:按钮）")
    parent_id: Optional[int] = Field(None, ge=0, description="父菜单ID")
    
    path: Optional[str] = Field(None, max_length=200, description="路由路径")
    component: Optional[str] = Field(None, max_length=255, description="组件路径")
    query: Optional[str] = Field(None, max_length=255, description="路由参数")
    
    perms: Optional[str] = Field(None, max_length=100, description="权限标识")
    
    icon: Optional[str] = Field(None, max_length=100, description="菜单图标")
    order_num: Optional[int] = Field(None, ge=0, description="排序")
    visible: Optional[int] = Field(None, ge=0, le=1, description="是否可见")
    status: Optional[int] = Field(None, ge=0, le=1, description="菜单状态")
    
    is_frame: Optional[int] = Field(None, ge=0, le=1, description="是否为外链")
    is_cache: Optional[int] = Field(None, ge=0, le=1, description="是否缓存")
    
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class MenuOutSchema(TimestampSchema):
    """菜单输出Schema"""
    
    id: int = Field(..., description="菜单ID")
    menu_name: str = Field(..., description="菜单名称")
    menu_type: str = Field(..., description="菜单类型（M:目录 C:菜单 F:按钮）")
    parent_id: int = Field(..., description="父菜单ID")
    
    path: Optional[str] = Field(None, description="路由路径")
    component: Optional[str] = Field(None, description="组件路径")
    query: Optional[str] = Field(None, description="路由参数")
    
    perms: Optional[str] = Field(None, description="权限标识")
    
    icon: Optional[str] = Field(None, description="菜单图标")
    order_num: int = Field(..., description="排序")
    visible: int = Field(..., description="是否可见")
    status: int = Field(..., description="菜单状态")
    
    is_frame: int = Field(..., description="是否为外链")
    is_cache: int = Field(..., description="是否缓存")
    
    remark: Optional[str] = Field(None, description="备注")
    
    children: Optional[List['MenuOutSchema']] = Field(default=[], description="子菜单列表")
    
    class Config:
        from_attributes = True


class MenuTreeSchema(BaseSchema):
    """菜单树Schema"""
    
    id: int = Field(..., description="菜单ID")
    label: str = Field(..., description="菜单名称")
    parent_id: int = Field(..., description="父菜单ID")
    menu_type: int = Field(..., description="菜单类型")
    children: Optional[List['MenuTreeSchema']] = Field(None, description="子菜单")


class MenuRouteSchema(BaseSchema):
    """前端路由Schema"""
    
    path: str = Field(..., description="路由路径")
    name: str = Field(..., description="路由名称")
    component: Optional[str] = Field(None, description="组件路径")
    redirect: Optional[str] = Field(None, description="重定向路径")
    
    meta: dict = Field(..., description="路由元信息")
    children: Optional[List['MenuRouteSchema']] = Field(None, description="子路由")
