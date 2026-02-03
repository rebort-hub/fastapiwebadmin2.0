"""
用户业务逻辑层
"""

from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.v1.system.user.crud import UserCRUD
from app.api.v1.system.user.schema import (
    UserCreateSchema,
    UserUpdateSchema,
    UserOutSchema,
    UserQuerySchema,
    UserPasswordSchema,
    UserResetPasswordSchema,
    UserProfileUpdateSchema,
    UserAvatarUpdateSchema
)
from app.api.v1.system.user.model import UserModel
from app.common.response import page_response
from app.utils.security import get_password_hash, verify_password


class UserService:
    """用户服务"""
    
    @classmethod
    async def get_user_detail_service(
        cls,
        user_id: int,
        db: AsyncSession
    ) -> UserOutSchema:
        """
        获取用户详情
        
        Args:
            user_id: 用户ID
            db: 数据库会话
            
        Returns:
            用户详情
        """
        crud = UserCRUD(db)
        user = await crud.get_by_id_crud(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 构建输出数据
        user_data = UserOutSchema.model_validate(user)
        user_data.role_ids = [role.id for role in user.roles] if user.roles else []
        user_data.role_names = [role.role_name for role in user.roles] if user.roles else []
        user_data.dept_name = user.dept.dept_name if user.dept else None
        
        return user_data
    
    @classmethod
    async def get_user_list_service(
        cls,
        query: UserQuerySchema,
        db: AsyncSession
    ) -> dict:
        """
        获取用户列表
        
        Args:
            query: 查询参数
            db: 数据库会话
            
        Returns:
            分页数据
        """
        crud = UserCRUD(db)
        
        # 构建查询条件
        conditions = []
        if query.username:
            conditions.append(UserModel.username.like(f"%{query.username}%"))
        if query.nickname:
            conditions.append(UserModel.nickname.like(f"%{query.nickname}%"))
        if query.phone:
            conditions.append(UserModel.phone.like(f"%{query.phone}%"))
        if query.email:
            conditions.append(UserModel.email.like(f"%{query.email}%"))
        if query.status is not None:
            conditions.append(UserModel.status == query.status)
        if query.user_type is not None:
            conditions.append(UserModel.user_type == query.user_type)
        if query.dept_id:
            conditions.append(UserModel.dept_id == query.dept_id)
        if query.begin_time:
            conditions.append(UserModel.created_at >= query.begin_time)
        if query.end_time:
            conditions.append(UserModel.created_at <= query.end_time)
        
        # 排序
        order_by = [UserModel.id.desc()]
        
        # 查询数据
        items, total = await crud.get_list_crud(
            conditions=conditions,
            order_by=order_by,
            skip=query.skip,
            limit=query.limit
        )
        
        # 转换为输出格式
        user_list = []
        for user in items:
            user_data = UserOutSchema.model_validate(user)
            user_data.role_ids = [role.id for role in user.roles] if user.roles else []
            user_data.role_names = [role.role_name for role in user.roles] if user.roles else []
            user_data.dept_name = user.dept.dept_name if user.dept else None
            user_list.append(user_data.model_dump())
        
        return page_response(
            items=user_list,
            total=total,
            page=query.page,
            page_size=query.page_size
        )

    @classmethod
    async def create_user_service(
        cls,
        data: UserCreateSchema,
        current_user_id: int,
        db: AsyncSession
    ) -> UserOutSchema:
        """
        创建用户
        
        Args:
            data: 用户数据
            current_user_id: 当前用户ID
            db: 数据库会话
            
        Returns:
            新创建的用户
        """
        crud = UserCRUD(db)
        
        # 检查用户名是否存在
        if await crud.check_username_exists_crud(data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否存在
        if data.email and await crud.check_email_exists_crud(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
        
        # 检查手机号是否存在
        if data.phone and await crud.check_phone_exists_crud(data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已存在"
            )
        
        # 准备数据
        user_data = data.model_dump(exclude={'role_ids', 'password'})
        user_data['password'] = get_password_hash(data.password)  # 加密密码
        user_data['created_by'] = current_user_id
        user_data['updated_by'] = current_user_id
        
        # 创建用户
        user = await crud.create_crud(user_data)
        
        # 关联角色
        if data.role_ids:
            from app.api.v1.system.role.model import RoleModel
            from sqlalchemy import select
            stmt = select(RoleModel).where(RoleModel.id.in_(data.role_ids))
            result = await db.execute(stmt)
            roles = result.scalars().all()
            user.roles = list(roles)
            await db.commit()
        
        return await cls.get_user_detail_service(user.id, db)
    
    @classmethod
    async def update_user_service(
        cls,
        user_id: int,
        data: UserUpdateSchema,
        current_user_id: int,
        db: AsyncSession
    ) -> UserOutSchema:
        """
        更新用户
        
        Args:
            user_id: 用户ID
            data: 更新数据
            current_user_id: 当前用户ID
            db: 数据库会话
            
        Returns:
            更新后的用户
        """
        crud = UserCRUD(db)
        
        # 检查用户是否存在
        user = await crud.get_by_id_crud(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查用户名是否重复
        if data.username and await crud.check_username_exists_crud(data.username, user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否重复
        if data.email and await crud.check_email_exists_crud(data.email, user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
        
        # 检查手机号是否重复
        if data.phone and await crud.check_phone_exists_crud(data.phone, user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已存在"
            )
        
        # 准备更新数据
        update_data = data.model_dump(exclude_unset=True, exclude={'role_ids', 'password'})
        update_data['updated_by'] = current_user_id
        
        # 如果提供了密码，单独处理（加密）
        if data.password:
            update_data['password'] = get_password_hash(data.password)
        
        # 更新用户基本信息
        if update_data:
            await crud.update_crud(user_id, update_data)
        
        # 更新角色关联
        if data.role_ids is not None:
            from app.api.v1.system.role.model import RoleModel
            from sqlalchemy import select
            stmt = select(RoleModel).where(RoleModel.id.in_(data.role_ids))
            result = await db.execute(stmt)
            roles = result.scalars().all()
            user.roles = list(roles)
            await db.commit()
        
        return await cls.get_user_detail_service(user_id, db)
    
    @classmethod
    async def delete_user_service(
        cls,
        user_ids: List[int],
        db: AsyncSession
    ) -> None:
        """
        删除用户
        
        Args:
            user_ids: 用户ID列表
            db: 数据库会话
        """
        crud = UserCRUD(db)
        
        # 检查是否包含超级管理员
        for user_id in user_ids:
            user = await crud.get_by_id_crud(user_id)
            if user and user.user_type == 10:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"不能删除超级管理员【{user.username}】"
                )
        
        # 先删除用户角色关联
        from sqlalchemy import delete as sql_delete
        from app.api.v1.system.user.model import user_role
        stmt = sql_delete(user_role).where(user_role.c.user_id.in_(user_ids))
        await db.execute(stmt)
        await db.commit()
        
        # 再删除用户
        await crud.delete_crud(user_ids)
    
    @classmethod
    async def change_password_service(
        cls,
        user_id: int,
        data: UserPasswordSchema,
        db: AsyncSession
    ) -> None:
        """
        修改密码
        
        Args:
            user_id: 用户ID
            data: 密码数据
            db: 数据库会话
        """
        crud = UserCRUD(db)
        
        # 获取用户
        user = await crud.get_by_id_crud(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证旧密码
        if not verify_password(data.old_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码不正确"
            )
        
        # 更新密码
        hashed_password = get_password_hash(data.new_password)
        await crud.update_password_crud(user_id, hashed_password)
    
    @classmethod
    async def reset_password_service(
        cls,
        user_id: int,
        data: UserResetPasswordSchema,
        db: AsyncSession
    ) -> None:
        """
        重置密码（管理员操作）
        
        Args:
            user_id: 用户ID
            data: 新密码数据
            db: 数据库会话
        """
        crud = UserCRUD(db)
        
        # 检查用户是否存在
        user = await crud.get_by_id_crud(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 更新密码
        hashed_password = get_password_hash(data.new_password)
        await crud.update_password_crud(user_id, hashed_password)
    
    @classmethod
    async def update_status_service(
        cls,
        user_id: int,
        status: int,
        db: AsyncSession
    ) -> None:
        """
        更新用户状态
        
        Args:
            user_id: 用户ID
            status: 状态（0:禁用 1:启用）
            db: 数据库会话
        """
        crud = UserCRUD(db)
        
        # 检查用户是否存在
        user = await crud.get_by_id_crud(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 不能禁用超级管理员
        if user.user_type == 10 and status == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能禁用超级管理员"
            )
        
        # 更新状态
        await crud.update_crud(user_id, {"status": status})

    
    @classmethod
    async def update_profile_service(
        cls,
        user_id: int,
        data: 'UserProfileUpdateSchema',
        db: AsyncSession
    ) -> UserOutSchema:
        """
        更新个人信息
        
        Args:
            user_id: 用户ID
            data: 个人信息数据
            db: 数据库会话
            
        Returns:
            更新后的用户信息
        """
        crud = UserCRUD(db)
        
        # 检查用户是否存在
        user = await crud.get_by_id_crud(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 准备更新数据（只更新允许的字段）
        update_data = {}
        if data.nickname is not None:
            update_data['nickname'] = data.nickname
        if data.remarks is not None:
            # 前端使用remarks，后端使用remark
            update_data['remark'] = data.remarks
        if data.email is not None:
            update_data['email'] = data.email
        if data.tags is not None:
            update_data['tags'] = data.tags
        
        # 更新用户信息
        if update_data:
            update_data['updated_at'] = datetime.now()
            await crud.update_crud(user_id, update_data)
        
        # 返回更新后的用户信息
        return await cls.get_user_detail_service(user_id, db)
    
    @classmethod
    async def update_avatar_service(
        cls,
        user_id: int,
        data: 'UserAvatarUpdateSchema',
        db: AsyncSession
    ) -> UserOutSchema:
        """
        更新用户头像
        
        Args:
            user_id: 用户ID
            data: 头像数据
            db: 数据库会话
            
        Returns:
            更新后的用户信息
        """
        import os
        import uuid
        import base64
        from pathlib import Path
        
        crud = UserCRUD(db)
        
        # 检查用户是否存在
        user = await crud.get_by_id_crud(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        avatar_url = data.avatar
        
        # 如果是base64数据，保存为文件
        if data.avatar.startswith('data:image/'):
            try:
                # 解析base64数据
                header, base64_data = data.avatar.split(',', 1)
                image_type = header.split('/')[1].split(';')[0]  # 获取图片类型 (jpeg, png等)
                
                # 生成唯一文件名
                filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}.{image_type}"
                
                # 创建头像目录
                avatar_dir = Path("static/upload/avatars")
                avatar_dir.mkdir(parents=True, exist_ok=True)
                
                # 保存文件
                file_path = avatar_dir / filename
                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(base64_data))
                
                # 生成访问URL
                avatar_url = f"/static/upload/avatars/{filename}"
                
                # 删除旧头像文件（如果存在且是本地文件）
                if user.avatar and user.avatar.startswith('/static/upload/avatars/'):
                    old_file_path = Path(user.avatar.lstrip('/'))
                    if old_file_path.exists():
                        try:
                            old_file_path.unlink()
                        except Exception as e:
                            print(f"删除旧头像文件失败: {e}")
                
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"头像处理失败: {str(e)}"
                )
        
        # 更新头像URL
        update_data = {
            'avatar': avatar_url,
            'updated_at': datetime.now()
        }
        await crud.update_crud(user_id, update_data)
        
        # 返回更新后的用户信息
        return await cls.get_user_detail_service(user_id, db)
