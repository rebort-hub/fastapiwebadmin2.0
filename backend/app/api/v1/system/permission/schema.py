"""
权限数据验证模型
"""

from typing import Optional
from pydantic import Field
from app.core.base_schema import BaseSchema, PageQuerySchema, TimestampSchema


class PermissionCreateSchema(BaseSchema):
    """权限创建Schema"""
    
    permission_name: str = Field(..., min_length=1, max_length=100, description="权限名称")
    permission_code: str = Field(..., min_length=1, max_length=100, description="权限编码")
    permission_type: int = Field(..., ge=1, le=4, description="权限类型")
    
    resource_type: Optional[str] = Field(None, max_length=50, description="资源类型")
    resource_id: Optional[int] = Field(None, description="关联资源ID")
    
    status: int = Field(1, ge=0, le=1, description="状态")
    description: Optional[str] = Field(None, max_length=500, description="描述")


class PermissionUpdateSchema(BaseSchema):
    """权限更新Schema"""
    
    permission_name: Optional[str] = Field(None, min_length=1, max_length=100, description="权限名称")
    permission_code: Optional[str] = Field(None, min_length=1, max_length=100, description="权限编码")
    permission_type: Optional[int] = Field(None, ge=1, le=4, description="权限类型")
    
    resource_type: Optional[str] = Field(None, max_length=50, description="资源类型")
    resource_id: Optional[int] = Field(None, description="关联资源ID")
    
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")
    description: Optional[str] = Field(None, max_length=500, description="描述")


class PermissionOutSchema(TimestampSchema):
    """权限输出Schema"""
    
    id: int = Field(..., description="权限ID")
    permission_name: str = Field(..., description="权限名称")
    permission_code: str = Field(..., description="权限编码")
    permission_type: int = Field(..., description="权限类型")
    
    resource_type: Optional[str] = Field(None, description="资源类型")
    resource_id: Optional[int] = Field(None, description="关联资源ID")
    
    status: int = Field(..., description="状态")
    description: Optional[str] = Field(None, description="描述")


class PermissionQuerySchema(PageQuerySchema):
    """权限查询Schema"""
    
    permission_name: Optional[str] = Field(None, description="权限名称（模糊查询）")
    permission_code: Optional[str] = Field(None, description="权限编码（模糊查询）")
    permission_type: Optional[int] = Field(None, ge=1, le=4, description="权限类型")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")
