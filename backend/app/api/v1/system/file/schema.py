"""
文件管理数据验证模型
"""

from typing import Optional, List
from datetime import datetime
from pydantic import Field, field_validator
from app.core.base_schema import BaseSchema, PageQuerySchema, TimestampSchema


class FileUploadSchema(BaseSchema):
    """文件上传Schema"""
    
    description: Optional[str] = Field(None, max_length=500, description="文件描述")
    tags: Optional[str] = Field(None, max_length=500, description="文件标签")
    is_public: int = Field(1, ge=0, le=1, description="是否公开（0:私有 1:公开）")


class FileUpdateSchema(BaseSchema):
    """文件更新Schema"""
    
    original_name: Optional[str] = Field(None, max_length=255, description="原始文件名")
    description: Optional[str] = Field(None, max_length=500, description="文件描述")
    tags: Optional[str] = Field(None, max_length=500, description="文件标签")
    is_public: Optional[int] = Field(None, ge=0, le=1, description="是否公开")


class FileOutSchema(TimestampSchema):
    """文件输出Schema"""
    
    id: int = Field(..., description="文件ID")
    file_name: str = Field(..., description="存储的文件名")
    original_name: str = Field(..., description="原始文件名")
    file_path: str = Field(..., description="文件路径")
    file_url: Optional[str] = Field(None, description="文件访问URL")
    
    file_size: int = Field(..., description="文件大小（字节）")
    file_type: Optional[str] = Field(None, description="文件MIME类型")
    file_ext: Optional[str] = Field(None, description="文件扩展名")
    
    upload_type: str = Field(..., description="上传类型")
    storage_path: Optional[str] = Field(None, description="存储路径")
    
    description: Optional[str] = Field(None, description="文件描述")
    tags: Optional[str] = Field(None, description="文件标签")
    
    download_count: int = Field(..., description="下载次数")
    is_public: int = Field(..., description="是否公开")
    
    uploaded_by: int = Field(..., description="上传用户ID")
    uploaded_at: datetime = Field(..., description="上传时间")
    
    # 格式化的文件大小
    formatted_size: Optional[str] = Field(None, description="格式化的文件大小")


class FileQuerySchema(PageQuerySchema):
    """文件查询Schema"""
    
    file_name: Optional[str] = Field(None, description="文件名（模糊查询）")
    original_name: Optional[str] = Field(None, description="原始文件名（模糊查询）")
    file_type: Optional[str] = Field(None, description="文件类型")
    file_ext: Optional[str] = Field(None, description="文件扩展名")
    upload_type: Optional[str] = Field(None, description="上传类型")
    is_public: Optional[int] = Field(None, ge=0, le=1, description="是否公开")
    uploaded_by: Optional[int] = Field(None, description="上传用户ID")
    begin_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    tags: Optional[str] = Field(None, description="标签（模糊查询）")


class FileBatchDeleteSchema(BaseSchema):
    """批量删除文件Schema"""
    
    ids: List[int] = Field(..., min_items=1, description="文件ID列表")


class FileUrlSchema(BaseSchema):
    """文件URL Schema"""
    
    file_url: str = Field(..., description="文件访问URL")
    download_url: str = Field(..., description="文件下载URL")
    expires_at: Optional[datetime] = Field(None, description="URL过期时间")


class FileUploadResponseSchema(BaseSchema):
    """文件上传响应Schema"""
    
    id: int = Field(..., description="文件ID")
    file_name: str = Field(..., description="存储的文件名")
    original_name: str = Field(..., description="原始文件名")
    file_path: str = Field(..., description="文件路径")
    file_url: str = Field(..., description="文件访问URL")
    file_size: int = Field(..., description="文件大小（字节）")
    file_type: str = Field(..., description="文件MIME类型")
    upload_type: str = Field(..., description="上传类型")
    uploaded_at: datetime = Field(..., description="上传时间")