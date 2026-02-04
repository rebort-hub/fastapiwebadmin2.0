"""
认证授权业务逻辑层
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from jose import JWTError, jwt
from app.api.v1.system.auth.schema import (
    LoginSchema,
    LoginResponseSchema,
    UserInfoSchema,
    RefreshTokenSchema,
    ChangePasswordSchema,
    RegisterSchema
)
from app.api.v1.system.user.crud import UserCRUD
from app.utils.security import verify_password, get_password_hash
from app.common.constants import TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

# JWT配置（实际项目中应该从配置文件读取）
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"


class AuthService:
    """认证授权服务"""
    
    @classmethod
    def create_access_token(
        cls,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建访问令牌
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            
        Returns:
            JWT令牌
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    @classmethod
    def create_refresh_token(
        cls,
        data: dict
    ) -> str:
        """
        创建刷新令牌
        
        Args:
            data: 要编码的数据
            
        Returns:
            JWT刷新令牌
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    @classmethod
    def verify_token(cls, token: str) -> dict:
        """
        验证令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            解码后的数据
            
        Raises:
            HTTPException: 令牌无效或过期
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌无效或已过期",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @classmethod
    async def login_service(
        cls,
        data: LoginSchema,
        client_ip: str,
        request,  # 添加request参数
        db: AsyncSession
    ) -> LoginResponseSchema:
        """
        用户登录
        
        Args:
            data: 登录数据
            client_ip: 客户端IP地址
            request: 请求对象
            db: 数据库会话
            
        Returns:
            登录响应（包含令牌）
        """
        from app.api.v1.system.log.service import LoginLogService
        from app.api.v1.monitor.online.service import OnlineUserService
        from app.utils.common import get_str_uuid
        
        crud = UserCRUD(db)
        
        # 获取用户
        user = await crud.get_by_username_crud(data.username)
        
        # 验证用户存在
        if not user:
            # 记录登录失败日志
            await LoginLogService.create_login_log(
                request=request,
                username=data.username,
                user_id=None,
                status=0,
                message="用户名不存在",
                db=db
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 验证密码
        if not verify_password(data.password, user.password):
            # 记录登录失败日志
            await LoginLogService.create_login_log(
                request=request,
                username=data.username,
                user_id=user.id,
                status=0,
                message="密码错误",
                db=db
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 验证用户状态
        if user.status != 1:
            # 记录登录失败日志
            await LoginLogService.create_login_log(
                request=request,
                username=data.username,
                user_id=user.id,
                status=0,
                message="用户已被禁用",
                db=db
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户已被禁用"
            )
        
        # 生成会话ID
        session_id = get_str_uuid()
        
        # 创建访问令牌（包含session_id）
        access_token = cls.create_access_token(
            data={"sub": str(user.id), "username": user.username, "session_id": session_id}
        )
        
        # 创建刷新令牌
        refresh_token = cls.create_refresh_token(
            data={"sub": str(user.id), "username": user.username, "session_id": session_id}
        )
        
        # 更新登录信息
        await crud.update_login_info_crud(
            user.id,
            datetime.now(),
            client_ip
        )
        
        # 记录登录成功日志
        await LoginLogService.create_login_log(
            request=request,
            username=data.username,
            user_id=user.id,
            status=1,
            message="登录成功",
            db=db
        )
        
        # 清理该用户的旧会话（同一用户重新登录时）
        try:
            from app.api.v1.monitor.online.service import OnlineUserService
            await OnlineUserService.force_offline(user.id)
        except Exception as e:
            print(f"[在线用户] 清理旧会话失败: {e}")
        
        # 添加在线用户记录
        try:
            user_agent = request.headers.get("user-agent", "")
            await OnlineUserService.add_online_user(
                user_id=user.id,
                username=user.username,
                nickname=user.nickname,
                avatar=user.avatar,
                session_id=session_id,
                ip_address=client_ip,
                user_agent=user_agent
            )
        except Exception as e:
            print(f"[在线用户] 添加在线用户失败: {e}")
        
        return LoginResponseSchema(
            access_token=access_token,
            token_type="Bearer",
            expires_in=TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=refresh_token
        )
    
    @classmethod
    async def get_current_user_service(
        cls,
        token: str,
        db: AsyncSession
    ) -> UserInfoSchema:
        """
        获取当前用户信息
        
        Args:
            token: JWT令牌
            db: 数据库会话
            
        Returns:
            用户信息
        """
        # 验证令牌
        payload = cls.verify_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌无效"
            )
        
        # 获取用户
        crud = UserCRUD(db)
        user = await crud.get_by_id_crud(int(user_id))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证用户状态
        if user.status != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户已被禁用"
            )
        
        # 获取角色列表
        roles = [role.role_key for role in user.roles] if user.roles else []
        
        # 获取权限列表
        permissions = []
        if user.roles:
            for role in user.roles:
                if role.menus:
                    for menu in role.menus:
                        if menu.perms:
                            permissions.append(menu.perms)
        
        # 去重
        permissions = list(set(permissions))
        
        return UserInfoSchema(
            id=user.id,
            username=user.username,
            nickname=user.nickname,
            email=user.email,
            phone=user.phone,
            avatar=user.avatar,
            user_type=user.user_type,
            dept_id=user.dept_id,
            dept_name=user.dept.dept_name if user.dept else None,
            roles=roles,
            permissions=permissions
        )
    
    @classmethod
    async def get_user_menus_service(
        cls,
        token: str,
        db: AsyncSession
    ) -> list:
        """
        获取当前用户菜单
        
        Args:
            token: JWT令牌
            db: 数据库会话
            
        Returns:
            菜单树列表（前端路由格式）
        """
        # 验证令牌
        payload = cls.verify_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌无效"
            )
        
        # 获取用户
        crud = UserCRUD(db)
        user = await crud.get_by_id_crud(int(user_id))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证用户状态
        if user.status != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户已被禁用"
            )
        
        # 收集所有菜单
        menus_dict = {}
        
        if user.roles:
            for role in user.roles:
                if role.menus:
                    for menu in role.menus:
                        # 只返回菜单和目录，不返回按钮
                        if menu.menu_type in ['M', 'C'] and menu.status == 1 and menu.visible == 1:
                            if menu.id not in menus_dict:
                                # 生成路由name（去掉开头的/，并替换/为-）
                                route_name = menu.path.lstrip('/').replace('/', '-') if menu.path else f'menu_{menu.id}'
                                
                                # 转换为前端路由格式
                                menus_dict[menu.id] = {
                                    'path': menu.path or '',
                                    'name': route_name,
                                    'component': menu.component,
                                    'redirect': None,
                                    'meta': {
                                        'title': menu.menu_name,
                                        'isLink': menu.path if menu.is_frame == 0 else '',
                                        'isHide': menu.visible == 0,
                                        'isKeepAlive': menu.is_cache == 0,
                                        'isAffix': False,
                                        'isIframe': menu.is_frame == 0,
                                        'roles': [],
                                        'icon': menu.icon or '',
                                    },
                                    'children': [],
                                    # 保留原始数据用于调试
                                    '_raw': {
                                        'id': menu.id,
                                        'parent_id': menu.parent_id,
                                        'order_num': menu.order_num,
                                        'menu_type': menu.menu_type,
                                        'perms': menu.perms,
                                    }
                                }
        
        # 如果没有菜单，返回空列表
        if not menus_dict:
            return []
        
        # 构建菜单树
        menus_list = list(menus_dict.values())
        
        # 按order_num排序
        menus_list.sort(key=lambda x: x['_raw']['order_num'])
        
        # 构建树形结构
        menu_tree = []
        for menu in menus_list:
            if menu['_raw']['parent_id'] == 0:
                menu_tree.append(menu)
            else:
                # 查找父菜单
                parent = menus_dict.get(menu['_raw']['parent_id'])
                if parent:
                    parent['children'].append(menu)
        
        # 递归排序子菜单
        def sort_children(menu_list):
            for menu in menu_list:
                if menu['children']:
                    menu['children'].sort(key=lambda x: x['_raw']['order_num'])
                    sort_children(menu['children'])
        
        sort_children(menu_tree)
        
        # 移除调试数据
        def remove_raw(menu_list):
            for menu in menu_list:
                if '_raw' in menu:
                    del menu['_raw']
                if menu['children']:
                    remove_raw(menu['children'])
        
        remove_raw(menu_tree)
        
        return menu_tree
    
    @classmethod
    async def refresh_token_service(
        cls,
        data: RefreshTokenSchema,
        db: AsyncSession
    ) -> LoginResponseSchema:
        """
        刷新令牌
        
        Args:
            data: 刷新令牌数据
            db: 数据库会话
            
        Returns:
            新的令牌
        """
        # 验证刷新令牌
        payload = cls.verify_token(data.refresh_token)
        
        # 检查令牌类型
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )
        
        user_id = payload.get("sub")
        username = payload.get("username")
        session_id = payload.get("session_id")
        
        if not user_id or not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌无效"
            )
        
        # 验证用户存在且状态正常
        crud = UserCRUD(db)
        user = await crud.get_by_id_crud(int(user_id))
        
        if not user or user.status != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户不存在或已被禁用"
            )
        
        # 创建新的访问令牌（保持相同的session_id）
        access_token = cls.create_access_token(
            data={"sub": user_id, "username": username, "session_id": session_id}
        )
        
        # 创建新的刷新令牌（保持相同的session_id）
        refresh_token = cls.create_refresh_token(
            data={"sub": user_id, "username": username, "session_id": session_id}
        )
        
        return LoginResponseSchema(
            access_token=access_token,
            token_type="Bearer",
            expires_in=TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=refresh_token
        )
    
    @classmethod
    async def logout_service(
        cls,
        token: str,
        db: AsyncSession
    ) -> None:
        """
        用户登出
        
        Args:
            token: JWT令牌
            db: 数据库会话
        """
        from app.api.v1.monitor.online.service import OnlineUserService
        
        # 验证令牌
        payload = cls.verify_token(token)
        
        # 获取用户ID和会话ID
        user_id = payload.get("sub")
        session_id = payload.get("session_id")
        
        # 移除在线用户记录
        if user_id and session_id:
            await OnlineUserService.remove_online_user(int(user_id), session_id)
        
        # 实际项目中可以将令牌加入黑名单
        # 这里简单处理，只验证令牌有效性
        pass
    
    @classmethod
    async def change_password_service(
        cls,
        user_id: int,
        data: ChangePasswordSchema,
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
    async def register_service(
        cls,
        data: RegisterSchema,
        db: AsyncSession
    ) -> UserInfoSchema:
        """
        用户注册
        
        Args:
            data: 注册数据
            db: 数据库会话
            
        Returns:
            用户信息
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
        
        # 创建用户
        user_data = {
            "username": data.username,
            "password": get_password_hash(data.password),
            "nickname": data.nickname,
            "email": data.email,
            "phone": data.phone,
            "user_type": 0,  # 普通用户
            "status": 1,  # 启用
            "created_by": 0,  # 系统创建
            "updated_by": 0
        }
        
        user = await crud.create_crud(user_data)
        
        return UserInfoSchema(
            id=user.id,
            username=user.username,
            nickname=user.nickname,
            email=user.email,
            phone=user.phone,
            avatar=user.avatar,
            user_type=user.user_type,
            dept_id=user.dept_id,
            dept_name=None,
            roles=[],
            permissions=[]
        )
