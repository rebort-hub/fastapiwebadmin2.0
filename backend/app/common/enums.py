"""
枚举定义
"""

from enum import IntEnum


class ResponseCode(IntEnum):
    """响应状态码"""
    SUCCESS = 200
    ERROR = 500
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    BAD_REQUEST = 400


class UserType(IntEnum):
    """用户类型"""
    NORMAL = 0  # 普通用户
    ADMIN = 10  # 超级管理员


class DataScope(IntEnum):
    """数据权限范围"""
    SELF = 1  # 仅本人数据
    DEPT = 2  # 本部门数据
    DEPT_AND_CHILD = 3  # 本部门及以下数据
    ALL = 4  # 全部数据
    CUSTOM = 5  # 自定义数据


class EnabledFlag(IntEnum):
    """启用标志"""
    DISABLED = 0  # 禁用
    ENABLED = 1  # 启用


class MenuType(IntEnum):
    """菜单类型"""
    DIRECTORY = 0  # 目录
    MENU = 1  # 菜单
    BUTTON = 2  # 按钮


class GenderType(IntEnum):
    """性别类型"""
    UNKNOWN = 0  # 未知
    MALE = 1  # 男
    FEMALE = 2  # 女
