"""
角色数据验证模型
"""

from typing import Optional, List
from pydantic import Field, field_validator
from app.core.base_schema import BaseSchema, PageQuerySchema, TimestampSchema


class RoleCreateSchema(BaseSchema):
    """角色创建Schema"""
    
    role_name: str = Field(..., min_length=1, max_length=50, description="角色名称")
    role_key: str = Field(..., min_length=1, max_length=50, description="角色权限字符串")
    role_sort: int = Field(0, ge=0, description="显示顺序")
    data_scope: int = Field(1, ge=1, le=5, description="数据范围")
    status: int = Field(1, ge=0, le=1, description="角色状态")
    remark: Optional[str] = Field(None, max_length=500, description="备注")
    menu_ids: Optional[List[int]] = Field(None, description="菜单ID列表")
    dept_ids: Optional[List[int]] = Field(None, description="部门ID列表（自定义权限）")


class RoleUpdateSchema(BaseSchema):
    """角色更新Schema"""
    
    role_name: Optional[str] = Field(None, min_length=1, max_length=50, description="角色名称")
    role_key: Optional[str] = Field(None, min_length=1, max_length=50, description="角色权限字符串")
    role_sort: Optional[int] = Field(None, ge=0, description="显示顺序")
    data_scope: Optional[int] = Field(None, ge=1, le=5, description="数据范围")
    status: Optional[int] = Field(None, ge=0, le=1, description="角色状态")
    remark: Optional[str] = Field(None, max_length=500, description="备注")
    menu_ids: Optional[List[int]] = Field(None, description="菜单ID列表")
    dept_ids: Optional[List[int]] = Field(None, description="部门ID列表（自定义权限）")


class RoleOutSchema(TimestampSchema):
    """角色输出Schema"""
    
    id: int = Field(..., description="角色ID")
    role_name: str = Field(..., description="角色名称")
    role_key: str = Field(..., description="角色权限字符串")
    role_sort: int = Field(..., description="显示顺序")
    data_scope: int = Field(..., description="数据范围")
    status: int = Field(..., description="角色状态")
    remark: Optional[str] = Field(None, description="备注")
    menu_ids: Optional[List[int]] = Field(None, description="菜单ID列表")
    dept_ids: Optional[List[int]] = Field(None, description="部门ID列表")


class RoleQuerySchema(PageQuerySchema):
    """角色查询Schema"""
    
    role_name: Optional[str] = Field(None, description="角色名称（模糊查询）")
    role_key: Optional[str] = Field(None, description="角色权限字符串（模糊查询）")
    status: Optional[int] = Field(None, ge=0, le=1, description="角色状态")
    begin_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
