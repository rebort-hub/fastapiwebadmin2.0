"""
文件管理业务逻辑层
"""

import os
import uuid
from datetime import datetime
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.response import page_response


class FileService:
    """文件服务"""
    
    # 文件上传目录
    UPLOAD_DIR = "uploads"
    # 允许的文件类型
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip'}
    # 最大文件大小（10MB）
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    @classmethod
    async def upload_file_service(
        cls,
        file: UploadFile,
        current_user_id: int,
        db: AsyncSession
    ) -> dict:
        """上传文件"""
        
        # 检查文件大小
        content = await file.read()
        if len(content) > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小超过限制（最大10MB）"
            )
        
        # 检查文件类型
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型，允许的类型：{', '.join(cls.ALLOWED_EXTENSIONS)}"
            )
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        
        # 创建上传目录
        upload_path = os.path.join(cls.UPLOAD_DIR, datetime.now().strftime("%Y%m%d"))
        os.makedirs(upload_path, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_path, unique_filename)
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 返回文件信息
        return {
            "file_name": file.filename,
            "file_path": file_path,
            "file_size": len(content),
            "file_type": file.content_type,
            "upload_time": datetime.now().isoformat()
        }
    
    @classmethod
    async def get_file_list_service(
        cls,
        page: int,
        page_size: int,
        file_name: str,
        db: AsyncSession
    ) -> dict:
        """获取文件列表"""
        
        # 这里简化处理，实际项目中应该从数据库查询
        files = []
        total = 0
        
        return page_response(
            items=files,
            total=total,
            page=page,
            page_size=page_size
        )
    
    @classmethod
    async def delete_file_service(
        cls,
        file_id: int,
        db: AsyncSession
    ) -> None:
        """删除文件"""
        
        # 这里简化处理，实际项目中应该从数据库查询并删除文件
        pass
