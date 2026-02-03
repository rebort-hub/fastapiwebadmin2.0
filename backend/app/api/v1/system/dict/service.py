"""
数据字典业务逻辑层
"""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.v1.system.dict.crud import DictTypeCRUD, DictDataCRUD
from app.api.v1.system.dict.schema import (
    DictTypeCreateSchema,
    DictTypeUpdateSchema,
    DictTypeOutSchema,
    DictTypeQuerySchema,
    DictDataCreateSchema,
    DictDataUpdateSchema,
    DictDataOutSchema,
    DictDataQuerySchema
)
from app.api.v1.system.dict.model import DictTypeModel, DictDataModel
from app.common.response import page_response, success_response


class DictTypeService:
    """字典类型服务"""
    
    @classmethod
    async def get_dict_type_detail_service(
        cls,
        dict_type_id: int,
        db: AsyncSession
    ) -> DictTypeOutSchema:
        """获取字典类型详情"""
        crud = DictTypeCRUD(db)
        dict_type = await crud.get_by_id_crud(dict_type_id)
        
        if not dict_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="字典类型不存在"
            )
        
        return DictTypeOutSchema.model_validate(dict_type)
    
    @classmethod
    async def get_dict_type_list_service(
        cls,
        query: DictTypeQuerySchema,
        db: AsyncSession
    ) -> dict:
        """获取字典类型列表"""
        crud = DictTypeCRUD(db)
        
        # 构建查询条件
        conditions = []
        if query.dict_name:
            conditions.append(DictTypeModel.dict_name.like(f"%{query.dict_name}%"))
        if query.dict_type:
            conditions.append(DictTypeModel.dict_type.like(f"%{query.dict_type}%"))
        if query.status is not None:
            conditions.append(DictTypeModel.status == query.status)
        if query.begin_time:
            conditions.append(DictTypeModel.created_at >= query.begin_time)
        if query.end_time:
            conditions.append(DictTypeModel.created_at <= query.end_time)
        
        # 排序
        order_by = [DictTypeModel.id.desc()]
        
        # 查询数据
        items, total = await crud.get_list_crud(
            conditions=conditions,
            order_by=order_by,
            skip=query.skip,
            limit=query.limit
        )
        
        # 转换为输出格式
        dict_type_list = [
            DictTypeOutSchema.model_validate(item).model_dump()
            for item in items
        ]
        
        return page_response(
            items=dict_type_list,
            total=total,
            page=query.page,
            page_size=query.page_size
        )
    
    @classmethod
    async def create_dict_type_service(
        cls,
        data: DictTypeCreateSchema,
        current_user_id: int,
        db: AsyncSession
    ) -> DictTypeOutSchema:
        """创建字典类型"""
        crud = DictTypeCRUD(db)
        
        # 检查字典类型是否存在
        if await crud.check_type_exists_crud(data.dict_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="字典类型已存在"
            )
        
        # 准备数据
        dict_type_data = data.model_dump()
        dict_type_data['created_by'] = current_user_id
        dict_type_data['updated_by'] = current_user_id
        
        # 创建字典类型
        dict_type = await crud.create_crud(dict_type_data)
        
        return await cls.get_dict_type_detail_service(dict_type.id, db)
    
    @classmethod
    async def update_dict_type_service(
        cls,
        dict_type_id: int,
        data: DictTypeUpdateSchema,
        current_user_id: int,
        db: AsyncSession
    ) -> DictTypeOutSchema:
        """更新字典类型"""
        crud = DictTypeCRUD(db)
        
        # 检查字典类型是否存在
        dict_type = await crud.get_by_id_crud(dict_type_id)
        if not dict_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="字典类型不存在"
            )
        
        # 检查字典类型是否重复
        if data.dict_type and await crud.check_type_exists_crud(data.dict_type, dict_type_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="字典类型已存在"
            )
        
        # 准备更新数据
        update_data = data.model_dump(exclude_unset=True)
        update_data['updated_by'] = current_user_id
        
        # 更新字典类型
        await crud.update_crud(dict_type_id, update_data)
        
        return await cls.get_dict_type_detail_service(dict_type_id, db)
    
    @classmethod
    async def delete_dict_type_service(
        cls,
        dict_type_ids: List[int],
        db: AsyncSession
    ) -> None:
        """删除字典类型"""
        crud = DictTypeCRUD(db)
        data_crud = DictDataCRUD(db)
        
        for dict_type_id in dict_type_ids:
            # 检查字典类型是否存在
            dict_type = await crud.get_by_id_crud(dict_type_id)
            if not dict_type:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"字典类型ID {dict_type_id} 不存在"
                )
            
            # 检查是否有关联的字典数据
            dict_data_list = await data_crud.get_by_type_crud(dict_type.dict_type)
            if dict_data_list:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"字典类型【{dict_type.dict_name}】下有 {len(dict_data_list)} 条字典数据，不能删除"
                )
        
        # 删除字典类型
        await crud.delete_crud(dict_type_ids)


class DictDataService:
    """字典数据服务"""
    
    @classmethod
    async def get_dict_data_detail_service(
        cls,
        dict_data_id: int,
        db: AsyncSession
    ) -> DictDataOutSchema:
        """获取字典数据详情"""
        crud = DictDataCRUD(db)
        dict_data = await crud.get_by_id_crud(dict_data_id)
        
        if not dict_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="字典数据不存在"
            )
        
        return DictDataOutSchema.model_validate(dict_data)
    
    @classmethod
    async def get_dict_data_list_service(
        cls,
        query: DictDataQuerySchema,
        db: AsyncSession
    ) -> dict:
        """获取字典数据列表"""
        crud = DictDataCRUD(db)
        
        # 构建查询条件
        conditions = []
        if query.dict_label:
            conditions.append(DictDataModel.dict_label.like(f"%{query.dict_label}%"))
        if query.dict_type:
            conditions.append(DictDataModel.dict_type == query.dict_type)
        if query.status is not None:
            conditions.append(DictDataModel.status == query.status)
        
        # 排序
        order_by = [DictDataModel.dict_sort.asc(), DictDataModel.id.asc()]
        
        # 查询数据
        items, total = await crud.get_list_crud(
            conditions=conditions,
            order_by=order_by,
            skip=query.skip,
            limit=query.limit
        )
        
        # 转换为输出格式
        dict_data_list = [
            DictDataOutSchema.model_validate(item).model_dump()
            for item in items
        ]
        
        return page_response(
            items=dict_data_list,
            total=total,
            page=query.page,
            page_size=query.page_size
        )
    
    @classmethod
    async def get_dict_data_by_type_service(
        cls,
        dict_type: str,
        db: AsyncSession
    ) -> dict:
        """根据字典类型获取数据"""
        crud = DictDataCRUD(db)
        
        # 获取字典数据
        items = await crud.get_by_type_crud(dict_type)
        
        # 只返回启用的数据
        items = [item for item in items if item.status == 1]
        
        # 转换为输出格式
        dict_data_list = [
            DictDataOutSchema.model_validate(item).model_dump()
            for item in items
        ]
        
        return success_response(data=dict_data_list, message="查询成功")
    
    @classmethod
    async def create_dict_data_service(
        cls,
        data: DictDataCreateSchema,
        current_user_id: int,
        db: AsyncSession
    ) -> DictDataOutSchema:
        """创建字典数据"""
        crud = DictDataCRUD(db)
        type_crud = DictTypeCRUD(db)
        
        # 检查字典类型是否存在
        dict_type = await type_crud.get_by_type_crud(data.dict_type)
        if not dict_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="字典类型不存在"
            )
        
        # 准备数据
        dict_data_data = data.model_dump()
        dict_data_data['created_by'] = current_user_id
        dict_data_data['updated_by'] = current_user_id
        
        # 创建字典数据
        dict_data = await crud.create_crud(dict_data_data)
        
        return await cls.get_dict_data_detail_service(dict_data.id, db)
    
    @classmethod
    async def update_dict_data_service(
        cls,
        dict_data_id: int,
        data: DictDataUpdateSchema,
        current_user_id: int,
        db: AsyncSession
    ) -> DictDataOutSchema:
        """更新字典数据"""
        crud = DictDataCRUD(db)
        
        # 检查字典数据是否存在
        dict_data = await crud.get_by_id_crud(dict_data_id)
        if not dict_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="字典数据不存在"
            )
        
        # 准备更新数据
        update_data = data.model_dump(exclude_unset=True)
        update_data['updated_by'] = current_user_id
        
        # 更新字典数据
        await crud.update_crud(dict_data_id, update_data)
        
        return await cls.get_dict_data_detail_service(dict_data_id, db)
    
    @classmethod
    async def delete_dict_data_service(
        cls,
        dict_data_ids: List[int],
        db: AsyncSession
    ) -> None:
        """删除字典数据"""
        crud = DictDataCRUD(db)
        
        # 删除字典数据
        await crud.delete_crud(dict_data_ids)
