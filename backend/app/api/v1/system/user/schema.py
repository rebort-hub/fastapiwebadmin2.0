"""
用户数据验证模型
"""

from typing import Optional, List
from datetime import datetime
from pydantic import Field, field_validator, EmailStr
from app.core.base_schema import BaseSchema, PageQuerySchema, TimestampSchema


class UserCreateSchema(BaseSchema):
    """用户创建Schema"""
    
    username: str = Field(..., min_length=2, max_length=64, description="用户名")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    nickname: str = Field(..., min_length=1, max_length=255, description="用户昵称")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    avatar: Optional[str] = Field(None, description="头像URL")
    
    user_type: int = Field(20, ge=0, le=100, description="用户类型（0:系统用户 10:超级管理员 20:普通用户）")
    status: int = Field(1, ge=0, le=1, description="用户状态")
    gender: int = Field(0, ge=0, le=2, description="性别")
    
    dept_id: Optional[int] = Field(None, description="部门ID")
    post: Optional[str] = Field(None, max_length=100, description="岗位")
    remark: Optional[str] = Field(None, max_length=500, description="备注")
    
    role_ids: Optional[List[int]] = Field(None, description="角色ID列表")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """验证邮箱格式，空字符串转为None"""
        if v == '':
            return None
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """验证手机号格式"""
        if v and not v.isdigit():
            raise ValueError('手机号格式不正确')
        return v


class UserUpdateSchema(BaseSchema):
    """用户更新Schema"""
    
    username: Optional[str] = Field(None, min_length=2, max_length=64, description="用户名")
    password: Optional[str] = Field(None, min_length=6, max_length=20, description="密码（留空则不修改）")
    nickname: Optional[str] = Field(None, min_length=1, max_length=255, description="用户昵称")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    avatar: Optional[str] = Field(None, description="头像URL")
    
    user_type: Optional[int] = Field(None, ge=0, le=100, description="用户类型")
    status: Optional[int] = Field(None, ge=0, le=1, description="用户状态")
    gender: Optional[int] = Field(None, ge=0, le=2, description="性别")
    
    dept_id: Optional[int] = Field(None, description="部门ID")
    post: Optional[str] = Field(None, max_length=100, description="岗位")
    remark: Optional[str] = Field(None, max_length=500, description="备注")
    
    role_ids: Optional[List[int]] = Field(None, description="角色ID列表")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """验证邮箱格式，空字符串转为None"""
        if v == '':
            return None
        return v


class UserPasswordSchema(BaseSchema):
    """用户密码修改Schema"""
    
    old_password: str = Field(..., min_length=6, max_length=20, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=20, description="新密码")
    confirm_password: str = Field(..., min_length=6, max_length=20, description="确认密码")
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v):
        """验证密码强度"""
        if len(v) < 6:
            raise ValueError('密码长度不能少于6位')
        
        # 检查是否包含数字
        has_digit = any(c.isdigit() for c in v)
        # 检查是否包含字母
        has_letter = any(c.isalpha() for c in v)
        
        if not (has_digit and has_letter):
            raise ValueError('密码必须包含字母和数字')
        
        return v
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        """验证两次密码是否一致"""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('两次密码不一致')
        return v


class UserResetPasswordSchema(BaseSchema):
    """重置密码Schema"""
    
    new_password: str = Field(..., min_length=6, max_length=20, description="新密码")


class UserOutSchema(TimestampSchema):
    """用户输出Schema"""
    
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    nickname: str = Field(..., description="用户昵称")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    avatar: Optional[str] = Field(None, description="头像URL")
    
    user_type: int = Field(..., description="用户类型")
    status: int = Field(..., description="用户状态")
    gender: int = Field(..., description="性别")
    
    dept_id: Optional[int] = Field(None, description="部门ID")
    dept_name: Optional[str] = Field(None, description="部门名称")
    post: Optional[str] = Field(None, description="岗位")
    remark: Optional[str] = Field(None, description="备注")
    tags: Optional[List[str]] = Field(None, description="个性标签")
    
    last_login_time: Optional[datetime] = Field(None, description="最后登录时间")
    last_login_ip: Optional[str] = Field(None, description="最后登录IP")
    
    role_ids: Optional[List[int]] = Field(None, description="角色ID列表")
    role_names: Optional[List[str]] = Field(None, description="角色名称列表")


class UserQuerySchema(PageQuerySchema):
    """用户查询Schema"""
    
    username: Optional[str] = Field(None, description="用户名（模糊查询）")
    nickname: Optional[str] = Field(None, description="用户昵称（模糊查询）")
    phone: Optional[str] = Field(None, description="手机号（模糊查询）")
    email: Optional[str] = Field(None, description="邮箱（模糊查询）")
    status: Optional[int] = Field(None, ge=0, le=1, description="用户状态")
    user_type: Optional[int] = Field(None, ge=0, le=10, description="用户类型")
    dept_id: Optional[int] = Field(None, description="部门ID")
    begin_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")



class UserProfileUpdateSchema(BaseSchema):
    """用户个人信息更新Schema"""
    
    nickname: Optional[str] = Field(None, min_length=1, max_length=255, description="用户昵称")
    remarks: Optional[str] = Field(None, max_length=500, description="个人签名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    tags: Optional[List[str]] = Field(None, description="个性标签")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """验证邮箱格式，空字符串转为None"""
        if v == '':
            return None
        return v


class UserAvatarUpdateSchema(BaseSchema):
    """用户头像更新Schema"""
    
    avatar: str = Field(..., description="头像URL或base64")
