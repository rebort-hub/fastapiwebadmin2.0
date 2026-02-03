"""
文件管理API控制器
"""

from fastapi import APIRouter, UploadFile, File, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.sqlalchemy import get_db
from app.api.v1.common.file.service import FileService
from app.common.response import success_response

router = APIRouter()


@router.post("/upload", summary="上传文件")
async def upload_file(
    file: UploadFile = File(..., description="上传的文件"),
    db: AsyncSession = Depends(get_db)
):
    """上传文件"""
    current_user_id = 1  # 临时使用固定用户ID
    result = await FileService.upload_file_service(file, current_user_id, db)
    return success_response(data=result, message="上传成功")


@router.get("/list", summary="获取文件列表")
async def get_file_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    file_name: str = Query(None, description="文件名"),
    db: AsyncSession = Depends(get_db)
):
    """获取文件列表"""
    return await FileService.get_file_list_service(page, page_size, file_name, db)


@router.delete("/{file_id}", summary="删除文件")
async def delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除文件"""
    await FileService.delete_file_service(file_id, db)
    return success_response(message="删除成功")
