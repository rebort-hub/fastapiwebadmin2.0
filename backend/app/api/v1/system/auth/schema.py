"""
认证授权数据验证模型
"""

from typing import Optional, List
from pydantic import Field, field_validator
from app.core.base_schema import BaseSchema


class LoginSchema(BaseSchema):
    """登录Schema"""
    
    username: str = Field(..., min_length=2, max_length=64, description="用户名")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    captcha: Optional[str] = Field(None, max_length=10, description="验证码")
    captcha_key: Optional[str] = Field(None, description="验证码key")


class LoginResponseSchema(BaseSchema):
    """登录响应Schema"""
    
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field("Bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    refresh_token: Optional[str] = Field(None, description="刷新令牌")


class RefreshTokenSchema(BaseSchema):
    """刷新令牌Schema"""
    
    refresh_token: str = Field(..., description="刷新令牌")


class UserInfoSchema(BaseSchema):
    """用户信息Schema"""
    
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    nickname: str = Field(..., description="用户昵称")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    avatar: Optional[str] = Field(None, description="头像")
    user_type: int = Field(..., description="用户类型")
    dept_id: Optional[int] = Field(None, description="部门ID")
    dept_name: Optional[str] = Field(None, description="部门名称")
    
    roles: List[str] = Field(default_factory=list, description="角色列表")
    permissions: List[str] = Field(default_factory=list, description="权限列表")


class ChangePasswordSchema(BaseSchema):
    """修改密码Schema"""
    
    old_password: str = Field(..., min_length=6, max_length=20, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=20, description="新密码")
    confirm_password: str = Field(..., min_length=6, max_length=20, description="确认密码")
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        """验证两次密码是否一致"""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('两次密码不一致')
        return v


class RegisterSchema(BaseSchema):
    """注册Schema"""
    
    username: str = Field(..., min_length=2, max_length=64, description="用户名")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    nickname: str = Field(..., min_length=1, max_length=255, description="用户昵称")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    captcha: Optional[str] = Field(None, max_length=10, description="验证码")
    captcha_key: Optional[str] = Field(None, description="验证码key")
