"""
数据字典数据验证模型
"""

from typing import Optional, List
from pydantic import Field
from app.core.base_schema import BaseSchema, PageQuerySchema, TimestampSchema


# ==================== 字典类型 ====================

class DictTypeCreateSchema(BaseSchema):
    """字典类型创建Schema"""
    
    dict_name: str = Field(..., min_length=1, max_length=100, description="字典名称")
    dict_type: str = Field(..., min_length=1, max_length=100, description="字典类型")
    status: int = Field(1, ge=0, le=1, description="状态")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class DictTypeUpdateSchema(BaseSchema):
    """字典类型更新Schema"""
    
    dict_name: Optional[str] = Field(None, min_length=1, max_length=100, description="字典名称")
    dict_type: Optional[str] = Field(None, min_length=1, max_length=100, description="字典类型")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class DictTypeOutSchema(TimestampSchema):
    """字典类型输出Schema"""
    
    id: int = Field(..., description="字典类型ID")
    dict_name: str = Field(..., description="字典名称")
    dict_type: str = Field(..., description="字典类型")
    status: int = Field(..., description="状态")
    remark: Optional[str] = Field(None, description="备注")


class DictTypeQuerySchema(PageQuerySchema):
    """字典类型查询Schema"""
    
    dict_name: Optional[str] = Field(None, description="字典名称（模糊查询）")
    dict_type: Optional[str] = Field(None, description="字典类型（模糊查询）")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")
    begin_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")


# ==================== 字典数据 ====================

class DictDataCreateSchema(BaseSchema):
    """字典数据创建Schema"""
    
    dict_sort: int = Field(0, ge=0, description="字典排序")
    dict_label: str = Field(..., min_length=1, max_length=100, description="字典标签")
    dict_value: str = Field(..., min_length=1, max_length=100, description="字典键值")
    dict_type: str = Field(..., min_length=1, max_length=100, description="字典类型")
    css_class: Optional[str] = Field(None, max_length=100, description="样式属性")
    list_class: Optional[str] = Field(None, max_length=100, description="表格回显样式")
    is_default: int = Field(0, ge=0, le=1, description="是否默认")
    status: int = Field(1, ge=0, le=1, description="状态")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class DictDataUpdateSchema(BaseSchema):
    """字典数据更新Schema"""
    
    dict_sort: Optional[int] = Field(None, ge=0, description="字典排序")
    dict_label: Optional[str] = Field(None, min_length=1, max_length=100, description="字典标签")
    dict_value: Optional[str] = Field(None, min_length=1, max_length=100, description="字典键值")
    dict_type: Optional[str] = Field(None, min_length=1, max_length=100, description="字典类型")
    css_class: Optional[str] = Field(None, max_length=100, description="样式属性")
    list_class: Optional[str] = Field(None, max_length=100, description="表格回显样式")
    is_default: Optional[int] = Field(None, ge=0, le=1, description="是否默认")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class DictDataOutSchema(TimestampSchema):
    """字典数据输出Schema"""
    
    id: int = Field(..., description="字典数据ID")
    dict_sort: int = Field(..., description="字典排序")
    dict_label: str = Field(..., description="字典标签")
    dict_value: str = Field(..., description="字典键值")
    dict_type: str = Field(..., description="字典类型")
    css_class: Optional[str] = Field(None, description="样式属性")
    list_class: Optional[str] = Field(None, description="表格回显样式")
    is_default: int = Field(..., description="是否默认")
    status: int = Field(..., description="状态")
    remark: Optional[str] = Field(None, description="备注")


class DictDataQuerySchema(PageQuerySchema):
    """字典数据查询Schema"""
    
    dict_label: Optional[str] = Field(None, description="字典标签（模糊查询）")
    dict_type: Optional[str] = Field(None, description="字典类型")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")
