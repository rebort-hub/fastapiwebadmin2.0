# -*- coding: utf-8 -*-
# @author: rebort
"""
用户工具函数 - 已迁移到新架构

注意：此文件中的函数已被弃用，请使用新架构的认证依赖：
- 使用 app.api.v1.system.auth.dependencies.get_current_user 替代 current_user()
- 新架构使用JWT认证，不再依赖Redis存储用户信息
"""

import typing
import warnings

from app.exceptions.exceptions import AccessTokenFail


async def current_user(token: str = None) -> typing.Union[typing.Dict[typing.Text, typing.Any], None]:
    """
    根据token获取用户信息 - 已弃用
    
    警告：此函数已被弃用，请使用新架构的认证依赖：
    from app.api.v1.system.auth.dependencies import get_current_user
    """
    warnings.warn(
        "current_user() 函数已被弃用，请使用 app.api.v1.system.auth.dependencies.get_current_user",
        DeprecationWarning,
        stacklevel=2
    )
    raise AccessTokenFail("请使用新架构的JWT认证")
