"""init complete menus from db_init.sql

Revision ID: init_menus_001
Revises: rbac_refactor_001
Create Date: 2026-01-30 16:30:00.000000

完整初始化所有菜单数据，基于原始db_init.sql
- 将menu_type=10转换为2（菜单）
- 将menu_type=20转换为3（按钮）
- 将roles字段转换为permission字段
- 同步所有按钮权限到permission表
- 为管理员角色分配所有菜单和权限
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'init_menus_001'
down_revision = 'rbac_refactor_001'
branch_labels = None
depends_on = None


def upgrade():
    """完整初始化菜单数据"""
    
    conn = op.get_bind()
    
    # ========================================================================
    # 1. 首页 (ID=1, menu_type=10→2)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, sort, menu_type, 
                         creation_date, updation_date, enabled_flag, views, created_by, updated_by)
        VALUES (1, 0, '/home', 'home', 'home/index', '首页', 0, 0, 'ele-HomeFilled', 
                1, 1, 0, 1, 2, '2023-02-01 14:41:05', '2023-02-01 14:41:05', 1, 0, 1, 1)
    """))
    
    # ========================================================================
    # 2. 系统设置目录 (ID=28, menu_type=10→1因为parent_id=0)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views, created_by, updated_by)
        VALUES (28, 0, '/system', 'system', 'layout/routerView/parent', '系统设置', 0, 0, 'ele-BellFilled', 
                0, 0, 0, 60, 1, '/system/menu', NULL, '2026-01-17 14:06:12', 1, 0, 1, 1)
    """))
    
    # ========================================================================
    # 3. 菜单管理 (ID=29, menu_type=10→2)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, sort, menu_type,
                         creation_date, updation_date, enabled_flag, views, created_by, updated_by)
        VALUES (29, 28, '/system/menu', 'systemMenu', 'system/menu/index', '菜单管理', 0, 0, 'ele-Menu', 
                1, 0, 0, 1, 2, NULL, '2026-01-16 14:03:08', 1, 0, 1, 1)
    """))
    
    # ========================================================================
    # 4. 用户管理 (ID=30, menu_type=10→2)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, sort, menu_type,
                         creation_date, updation_date, enabled_flag, views, created_by, updated_by)
        VALUES (30, 28, '/system/user', 'systemUser', 'system/user/index', '用户管理', 0, 0, 'ele-User', 
                1, 0, 0, 2, 2, NULL, '2026-01-16 14:03:26', 1, 0, 1, 1)
    """))
    
    # ========================================================================
    # 5. 角色管理 (ID=31, menu_type=10→2)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views, created_by, updated_by)
        VALUES (31, 28, '/system/role', 'systemRole', 'system/role/index', '角色管理', 0, 0, 'ele-UserFilled', 
                1, 0, 0, 1, 2, '', '2022-03-11 16:43:26', '2026-01-16 14:03:18', 1, 0, 1, 1)
    """))
    
    # ========================================================================
    # 6. 数据字典 (ID=51, menu_type=10→2)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views, created_by, updated_by)
        VALUES (51, 28, '/system/lookup', 'systemLookup', 'system/lookup/index.vue', '数据字典', 0, 0, 'ele-Management', 
                1, 0, 0, 3, 2, '', '2022-05-03 17:11:59', '2026-01-16 14:03:34', 1, 0, 1, 1)
    """))
    
    # ========================================================================
    # 7. 个人中心 (ID=61, menu_type=10→2)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views, created_by, updated_by)
        VALUES (61, 28, '/system/personal', 'personal', 'system/personal/index', '个人中心', 0, 0, 'ele-User', 
                1, 0, 0, 60, 2, '', '2023-01-16 16:37:40', '2026-01-17 15:49:51', 1, 3, 1, 1)
    """))
    
    # ========================================================================
    # 8. 接口管理目录 (ID=63, menu_type=10→1)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views)
        VALUES (63, 0, '/apiDoc', 'apiDoc', 'layout', '接口管理', 0, 0, 'ele-BellFilled', 
                1, 0, 0, 90, 1, '/apiDoc/swagger', '2026-01-16 11:10:31', '2026-01-16 14:02:04', 1, 0)
    """))
    
    # ========================================================================
    # 9. Swagger文档 (ID=64, menu_type=10→2)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views)
        VALUES (64, 63, '/apiDoc/swagger', 'apiDocSwagger', '/system/apiDoc/swagger', 'Swagger文档', 0, 0, 'ele-ChatLineSquare', 
                1, 0, 0, 1, 2, '', '2026-01-16 11:13:22', '2026-01-16 14:02:12', 1, 0)
    """))
    
    # ========================================================================
    # 10. Redoc文档 (ID=65, menu_type=10→2)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views)
        VALUES (65, 63, '/apiDoc/redoc', 'apiDocRedoc', '/system/apiDoc/redoc', 'Redoc文档', 0, 0, 'ele-CreditCard', 
                1, 0, 0, 2, 2, '', '2026-01-16 11:15:28', '2026-01-16 14:02:20', 1, 0)
    """))
    
    # ========================================================================
    # 11. 文件管理 (ID=66, menu_type=10→2)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views)
        VALUES (66, 28, '/system/file', 'systemFile', '/system/file/index', '文件管理', 0, 0, 'ele-DocumentCopy', 
                1, 0, 0, 50, 2, '', '2026-01-16 11:39:11', '2026-01-16 14:03:52', 1, 0)
    """))
    
    # ========================================================================
    # 12. 系统监控 (ID=67, menu_type=10→2)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views)
        VALUES (67, 28, '/system/monitor', 'systemMonitor', '/system/monitor/index', '系统监控', 0, 0, 'ele-Platform', 
                1, 0, 0, 60, 2, '', '2026-01-16 11:41:17', '2026-01-16 13:47:00', 1, 0)
    """))
    
    # ========================================================================
    # 13. 系统登录记录 (ID=76, menu_type=10→2)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views, created_by, updated_by)
        VALUES (76, 0, '/system/loginRecord', 'loginRecord', 'system/loginRecord/index', '系统登录记录', 0, 0, 'ele-ChatDotSquare', 
                1, 0, 0, 60, 2, '', '2026-01-17 14:03:08', '2026-01-17 14:22:55', 1, 0, 1, 1)
    """))
    
    # ========================================================================
    # 14. 项目管理 (ID=77, menu_type=10→2)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views, created_by, updated_by)
        VALUES (77, 0, '/system/project', 'project', 'system/project/index', '项目管理', 0, 0, 'ele-DocumentCopy', 
                1, 0, 0, 1, 2, '', '2026-01-17 14:15:22', '2026-01-17 14:16:17', 1, 0, 1, 1)
    """))
    
    # ========================================================================
    # 15. 部门管理 (ID=78, menu_type=10→2)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views, created_by, updated_by)
        VALUES (78, 28, '/system/dept', 'dept', '/system/dept/index', '部门管理', 0, 0, 'ele-CreditCard', 
                1, 0, 0, 1, 2, '', '2026-01-17 15:11:42', '2026-01-17 15:15:01', 1, 0, 1, 1)
    """))
    
    # ========================================================================
    # 按钮权限 - 用户管理 (menu_type=20→3, roles→permission)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, permission, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views, created_by, updated_by)
        VALUES 
        (79, 30, '', 'user_query', '', '查询用户', 0, 0, '', 1, 0, 1, 'user:query', 1, 3, '', 
         '2026-01-17 16:18:47', '2026-01-17 18:03:03', 1, 0, 1, 1),
        (80, 30, '', 'user_add', '', '新增用户', 0, 0, '', 1, 0, 1, 'user:add', 2, 3, '', 
         '2026-01-17 16:19:13', '2026-01-17 18:03:10', 1, 0, 1, 1),
        (81, 30, '', 'user_edit', '', '编辑用户', 0, 0, '', 1, 0, 1, 'user:edit', 3, 3, '', 
         '2026-01-17 16:19:44', '2026-01-17 18:03:17', 1, 0, 1, 1),
        (82, 30, '', 'user_disable', '', '禁用用户', 0, 0, '', 1, 0, 1, 'user:disable', 4, 3, '', 
         '2026-01-17 16:20:15', '2026-01-17 18:03:25', 1, 0, 1, 1),
        (83, 30, '', 'user_resetpwd', '', '重置密码', 0, 0, '', 1, 0, 1, 'user:resetpwd', 5, 3, '', 
         '2026-01-17 16:21:01', '2026-01-17 18:03:32', 1, 0, 1, 1),
        (84, 30, '', 'user_delete', '', '删除用户', 0, 0, '', 1, 0, 1, 'user:delete', 6, 3, '', 
         '2026-01-17 16:21:32', '2026-01-17 18:03:40', 1, 0, 1, 1)
    """))
    
    # ========================================================================
    # 按钮权限 - 角色管理 (menu_type=20→3, roles→permission)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, permission, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views, created_by, updated_by)
        VALUES 
        (85, 31, '', 'role_query', '', '查询角色', 0, 0, '', 1, 0, 1, 'role:query', 1, 3, '', 
         '2026-01-17 16:23:55', '2026-01-17 18:04:15', 1, 0, 1, 1),
        (86, 31, '', 'role_add', '', '新增角色', 0, 0, '', 1, 0, 1, 'role:add', 2, 3, '', 
         '2026-01-17 16:24:20', '2026-01-17 18:04:20', 1, 0, 1, 1),
        (87, 31, '', 'role_edit', '', '编辑角色', 0, 0, '', 1, 0, 1, 'role:edit', 3, 3, '', 
         '2026-01-17 16:24:48', '2026-01-17 18:04:26', 1, 0, 1, 1),
        (88, 31, '', 'role_delete', '', '删除角色', 0, 0, '', 1, 0, 1, 'role:delete', 4, 3, '', 
         '2026-01-17 16:25:22', '2026-01-17 18:04:32', 1, 0, 1, 1)
    """))
    
    # ========================================================================
    # 按钮权限 - 部门管理 (menu_type=20→3, roles→permission)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, permission, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views, created_by, updated_by)
        VALUES 
        (89, 78, '', 'dept_add', '', '新增部门', 0, 0, '', 1, 0, 1, 'dept:add', 1, 3, '', 
         '2026-01-17 16:26:02', '2026-01-17 18:03:52', 1, 0, 1, 1),
        (90, 78, '', 'dept_edit', '', '编辑部门', 0, 0, '', 1, 0, 1, 'dept:edit', 2, 3, '', 
         '2026-01-17 16:26:22', '2026-01-17 18:03:58', 1, 0, 1, 1),
        (91, 78, '', 'dept_disable', '', '禁用部门', 0, 0, '', 1, 0, 1, 'dept:disable', 3, 3, '', 
         '2026-01-17 16:26:54', '2026-01-17 18:04:03', 1, 0, 1, 1),
        (92, 78, '', 'dept_delete', '', '删除部门', 0, 0, '', 1, 0, 1, 'dept:delete', 4, 3, '', 
         '2026-01-17 16:27:15', '2026-01-17 18:04:09', 1, 0, 1, 1)
    """))
    
    # ========================================================================
    # 按钮权限 - 项目管理 (menu_type=20→3, roles→permission)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, permission, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views, created_by, updated_by)
        VALUES 
        (93, 77, '', 'project_query', '', '查询项目', 0, 0, '', 1, 0, 1, 'project:query', 1, 3, '', 
         '2026-01-17 16:27:49', '2026-01-17 18:02:41', 1, 0, 1, 1),
        (94, 77, '', 'project_add', '', '新增项目', 0, 0, '', 1, 0, 1, 'project:add', 2, 3, '', 
         '2026-01-17 16:28:10', '2026-01-17 18:02:46', 1, 0, 1, 1),
        (95, 77, '', 'project_edit', '', '编辑项目', 0, 0, '', 1, 0, 1, 'project:edit', 3, 3, '', 
         '2026-01-17 16:28:32', '2026-01-17 18:02:51', 1, 0, 1, 1),
        (96, 77, '', 'project_delete', '', '删除项目', 0, 0, '', 1, 0, 1, 'project:delete', 4, 3, '', 
         '2026-01-17 16:28:53', '2026-01-17 18:02:55', 1, 0, 1, 1)
    """))
    
    # ========================================================================
    # 按钮权限 - 登录记录 (menu_type=20→3, roles→permission)
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO menu (id, parent_id, path, name, component, title, isLink, isHide, icon, 
                         isKeepAlive, isAffix, isIframe, permission, sort, menu_type, redirect,
                         creation_date, updation_date, enabled_flag, views, created_by, updated_by)
        VALUES 
        (97, 76, '', 'loginRecord_query', '', '查询记录', 0, 0, '', 1, 0, 1, 'loginRecord:query', 1, 3, '', 
         '2026-01-17 16:29:49', '2026-01-17 18:03:44', 1, 0, 1, 1)
    """))
    
    # ========================================================================
    # 同步所有按钮权限到permission表
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO permission (permission_code, permission_name, permission_type, 
                               resource_type, status, sort, creation_date, updation_date, enabled_flag)
        SELECT 
            permission as permission_code,
            title as permission_name,
            2 as permission_type,
            SUBSTRING_INDEX(permission, ':', 1) as resource_type,
            1 as status,
            sort,
            NOW() as creation_date,
            NOW() as updation_date,
            1 as enabled_flag
        FROM menu
        WHERE menu_type = 3 
        AND permission IS NOT NULL 
        AND permission != ''
        AND enabled_flag = 1
        ON DUPLICATE KEY UPDATE
            permission_name = VALUES(permission_name),
            sort = VALUES(sort),
            updation_date = NOW()
    """))
    
    # ========================================================================
    # 为管理员角色(ID=1)分配所有菜单
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO role_menu (role_id, menu_id, creation_date, updation_date, enabled_flag)
        SELECT 1, id, NOW(), NOW(), 1 
        FROM menu 
        WHERE enabled_flag = 1
        ON DUPLICATE KEY UPDATE updation_date = NOW()
    """))
    
    # ========================================================================
    # 为管理员角色(ID=1)分配所有权限
    # ========================================================================
    conn.execute(sa.text("""
        INSERT INTO role_permission (role_id, permission_id, creation_date, updation_date, enabled_flag)
        SELECT 1, id, NOW(), NOW(), 1 
        FROM permission 
        WHERE enabled_flag = 1
        ON DUPLICATE KEY UPDATE updation_date = NOW()
    """))


def downgrade():
    """回滚：删除所有初始化的菜单数据"""
    conn = op.get_bind()
    
    # 删除关联数据
    conn.execute(sa.text("DELETE FROM role_menu WHERE role_id = 1"))
    conn.execute(sa.text("DELETE FROM role_permission WHERE role_id = 1"))
    
    # 删除权限数据
    conn.execute(sa.text("DELETE FROM permission WHERE permission_type = 2"))
    
    # 删除菜单数据（按ID范围删除）
    conn.execute(sa.text("DELETE FROM menu WHERE id IN (1, 28, 29, 30, 31, 51, 61, 63, 64, 65, 66, 67, 76, 77, 78)"))
    conn.execute(sa.text("DELETE FROM menu WHERE id BETWEEN 79 AND 97"))
