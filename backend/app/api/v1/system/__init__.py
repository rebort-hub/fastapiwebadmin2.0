"""
系统管理模块
"""

from fastapi import APIRouter

# 创建系统管理路由
router = APIRouter()

# 导入子模块路由
from app.api.v1.system.auth.controller import router as auth_router
from app.api.v1.system.user.controller import router as user_router
from app.api.v1.system.role.controller import router as role_router
from app.api.v1.system.dept.controller import router as dept_router
from app.api.v1.system.menu.controller import router as menu_router
from app.api.v1.system.dict.controller import router as dict_router
from app.api.v1.system.permission.controller import router as permission_router
from app.api.v1.system.log.controller import router as log_router
from app.api.v1.system.file.controller import router as file_router

# 注册子路由
router.include_router(auth_router, prefix="/auth", tags=["认证授权"])
router.include_router(user_router, prefix="/user", tags=["用户管理"])
router.include_router(role_router, prefix="/role", tags=["角色管理"])
router.include_router(dept_router, prefix="/dept", tags=["部门管理"])
router.include_router(menu_router, prefix="/menu", tags=["菜单管理"])
router.include_router(dict_router, prefix="/dict", tags=["字典管理"])
router.include_router(permission_router, prefix="/permission", tags=["权限管理"])
router.include_router(log_router, prefix="/log", tags=["日志管理"])
router.include_router(file_router, prefix="/file", tags=["文件管理"])

__all__ = ["router"]
