"""create sys tables for new architecture

Revision ID: create_sys_tables
Revises: 793c2186dd5a
Create Date: 2026-01-31 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'create_sys_tables'
down_revision = 'fix_user_status_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 先创建没有外键依赖的表
    
    # 创建sys_dept表（没有外键依赖）
    op.create_table(
        'sys_dept',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
        sa.Column('dept_name', sa.String(100), nullable=False, comment='部门名称'),
        sa.Column('dept_code', sa.String(64), nullable=True, comment='部门编码'),
        sa.Column('parent_id', sa.Integer(), nullable=True, server_default='0', comment='父部门ID（0表示顶级部门）'),
        sa.Column('ancestors', sa.String(500), nullable=True, comment='祖级列表（逗号分隔）'),
        sa.Column('leader_id', sa.BigInteger(), nullable=True, comment='负责人ID'),
        sa.Column('phone', sa.String(20), nullable=True, comment='联系电话'),
        sa.Column('email', sa.String(100), nullable=True, comment='邮箱'),
        sa.Column('sort', sa.Integer(), nullable=True, server_default='0', comment='排序'),
        sa.Column('status', sa.Integer(), nullable=True, server_default='1', comment='状态（0:禁用 1:启用）'),
        sa.Column('description', sa.String(500), nullable=True, comment='部门描述'),
        sa.Column('creation_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('created_by', sa.BigInteger(), nullable=True, comment='创建人ID'),
        sa.Column('updation_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('updated_by', sa.BigInteger(), nullable=True, comment='更新人ID'),
        sa.Column('enabled_flag', sa.Boolean(), nullable=False, server_default='1', comment='是否删除, 0 删除 1 非删除'),
        sa.Column('trace_id', sa.String(255), nullable=True, comment='trace_id'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        comment='部门表'
    )
    op.create_index('ix_sys_dept_dept_code', 'sys_dept', ['dept_code'], unique=True)
    
    # 创建sys_user表（依赖sys_dept）
    op.create_table(
        'sys_user',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
        sa.Column('username', sa.String(64), nullable=False, comment='用户名'),
        sa.Column('password', sa.Text(), nullable=False, comment='密码（加密）'),
        sa.Column('nickname', sa.String(255), nullable=False, comment='用户昵称'),
        sa.Column('email', sa.String(64), nullable=True, comment='邮箱'),
        sa.Column('phone', sa.String(20), nullable=True, comment='手机号'),
        sa.Column('avatar', sa.Text(), nullable=True, comment='头像URL'),
        sa.Column('user_type', sa.Integer(), nullable=False, server_default='0', comment='用户类型（0:普通用户 10:超级管理员）'),
        sa.Column('status', sa.Integer(), nullable=False, server_default='1', comment='用户状态（0:禁用 1:启用）'),
        sa.Column('gender', sa.Integer(), nullable=True, server_default='0', comment='性别（0:未知 1:男 2:女）'),
        sa.Column('dept_id', sa.BigInteger(), nullable=True, comment='部门ID'),
        sa.Column('post', sa.String(100), nullable=True, comment='岗位'),
        sa.Column('remark', sa.String(500), nullable=True, comment='备注'),
        sa.Column('last_login_time', sa.DateTime(), nullable=True, comment='最后登录时间'),
        sa.Column('last_login_ip', sa.String(50), nullable=True, comment='最后登录IP'),
        sa.Column('creation_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('created_by', sa.BigInteger(), nullable=True, comment='创建人ID'),
        sa.Column('updation_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('updated_by', sa.BigInteger(), nullable=True, comment='更新人ID'),
        sa.Column('enabled_flag', sa.Boolean(), nullable=False, server_default='1', comment='是否删除, 0 删除 1 非删除'),
        sa.Column('trace_id', sa.String(255), nullable=True, comment='trace_id'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['dept_id'], ['sys_dept.id']),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        comment='用户表'
    )
    op.create_index('ix_sys_user_username', 'sys_user', ['username'], unique=True)
    
    # 现在添加dept表的leader_id外键（依赖sys_user）
    op.create_foreign_key(
        'fk_sys_dept_leader_id',
        'sys_dept', 'sys_user',
        ['leader_id'], ['id']
    )
    
    # 创建sys_role表
    op.create_table(
        'sys_role',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
        sa.Column('role_name', sa.String(50), nullable=False, comment='角色名称'),
        sa.Column('role_key', sa.String(50), nullable=False, comment='角色权限字符串'),
        sa.Column('role_sort', sa.Integer(), server_default='0', comment='显示顺序'),
        sa.Column('data_scope', sa.Integer(), server_default='1', comment='数据范围（1:仅本人 2:本部门 3:本部门及以下 4:全部 5:自定义）'),
        sa.Column('status', sa.Integer(), server_default='1', comment='角色状态（0:停用 1:正常）'),
        sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
        sa.Column('creation_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('created_by', sa.BigInteger(), nullable=True, comment='创建人ID'),
        sa.Column('updation_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('updated_by', sa.BigInteger(), nullable=True, comment='更新人ID'),
        sa.Column('enabled_flag', sa.Boolean(), nullable=False, server_default='1', comment='是否删除, 0 删除 1 非删除'),
        sa.Column('trace_id', sa.String(255), nullable=True, comment='trace_id'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        comment='角色表'
    )
    op.create_index('ix_sys_role_role_name', 'sys_role', ['role_name'], unique=True)
    op.create_index('ix_sys_role_role_key', 'sys_role', ['role_key'], unique=True)
    
    # 创建sys_menu表
    op.create_table(
        'sys_menu',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
        sa.Column('menu_name', sa.String(50), nullable=False, comment='菜单名称'),
        sa.Column('parent_id', sa.Integer(), nullable=True, server_default='0', comment='父菜单ID'),
        sa.Column('order_num', sa.Integer(), nullable=True, server_default='0', comment='显示顺序'),
        sa.Column('path', sa.String(200), nullable=True, comment='路由地址'),
        sa.Column('component', sa.String(255), nullable=True, comment='组件路径'),
        sa.Column('query', sa.String(255), nullable=True, comment='路由参数'),
        sa.Column('is_frame', sa.Integer(), server_default='1', comment='是否为外链（0:是 1:否）'),
        sa.Column('is_cache', sa.Integer(), server_default='0', comment='是否缓存（0:缓存 1:不缓存）'),
        sa.Column('menu_type', sa.String(1), nullable=False, comment='菜单类型（M:目录 C:菜单 F:按钮）'),
        sa.Column('visible', sa.Integer(), server_default='1', comment='菜单状态（0:隐藏 1:显示）'),
        sa.Column('status', sa.Integer(), server_default='1', comment='菜单状态（0:停用 1:正常）'),
        sa.Column('perms', sa.String(100), nullable=True, comment='权限标识'),
        sa.Column('icon', sa.String(100), nullable=True, comment='菜单图标'),
        sa.Column('remark', sa.String(500), nullable=True, comment='备注'),
        sa.Column('creation_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('created_by', sa.BigInteger(), nullable=True, comment='创建人ID'),
        sa.Column('updation_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('updated_by', sa.BigInteger(), nullable=True, comment='更新人ID'),
        sa.Column('enabled_flag', sa.Boolean(), nullable=False, server_default='1', comment='是否删除, 0 删除 1 非删除'),
        sa.Column('trace_id', sa.String(255), nullable=True, comment='trace_id'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        comment='菜单表'
    )
    
    # 创建sys_dict_type表
    op.create_table(
        'sys_dict_type',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
        sa.Column('dict_name', sa.String(100), nullable=False, comment='字典名称'),
        sa.Column('dict_type', sa.String(100), nullable=False, comment='字典类型'),
        sa.Column('status', sa.Integer(), nullable=True, server_default='1', comment='状态（0:禁用 1:启用）'),
        sa.Column('remark', sa.String(500), nullable=True, comment='备注'),
        sa.Column('creation_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('created_by', sa.BigInteger(), nullable=True, comment='创建人ID'),
        sa.Column('updation_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('updated_by', sa.BigInteger(), nullable=True, comment='更新人ID'),
        sa.Column('enabled_flag', sa.Boolean(), nullable=False, server_default='1', comment='是否删除, 0 删除 1 非删除'),
        sa.Column('trace_id', sa.String(255), nullable=True, comment='trace_id'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        comment='字典类型表'
    )
    op.create_index('ix_sys_dict_type_dict_type', 'sys_dict_type', ['dict_type'], unique=True)
    
    # 创建sys_dict_data表
    op.create_table(
        'sys_dict_data',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
        sa.Column('dict_sort', sa.Integer(), nullable=True, server_default='0', comment='字典排序'),
        sa.Column('dict_label', sa.String(100), nullable=False, comment='字典标签'),
        sa.Column('dict_value', sa.String(100), nullable=False, comment='字典键值'),
        sa.Column('dict_type', sa.String(100), nullable=False, comment='字典类型'),
        sa.Column('css_class', sa.String(100), nullable=True, comment='样式属性（CSS类名）'),
        sa.Column('list_class', sa.String(100), nullable=True, comment='表格回显样式'),
        sa.Column('is_default', sa.Integer(), nullable=True, server_default='0', comment='是否默认（0:否 1:是）'),
        sa.Column('status', sa.Integer(), nullable=True, server_default='1', comment='状态（0:禁用 1:启用）'),
        sa.Column('remark', sa.String(500), nullable=True, comment='备注'),
        sa.Column('creation_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('created_by', sa.BigInteger(), nullable=True, comment='创建人ID'),
        sa.Column('updation_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('updated_by', sa.BigInteger(), nullable=True, comment='更新人ID'),
        sa.Column('enabled_flag', sa.Boolean(), nullable=False, server_default='1', comment='是否删除, 0 删除 1 非删除'),
        sa.Column('trace_id', sa.String(255), nullable=True, comment='trace_id'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['dict_type'], ['sys_dict_type.dict_type']),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        comment='字典数据表'
    )
    op.create_index('ix_sys_dict_data_dict_type', 'sys_dict_data', ['dict_type'])
    
    # 创建sys_permission表
    op.create_table(
        'sys_permission',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
        sa.Column('permission_name', sa.String(100), nullable=False, comment='权限名称'),
        sa.Column('permission_code', sa.String(100), nullable=False, comment='权限编码'),
        sa.Column('permission_type', sa.Integer(), nullable=False, comment='权限类型（1:菜单 2:按钮 3:接口 4:数据）'),
        sa.Column('resource_type', sa.String(50), nullable=True, comment='资源类型'),
        sa.Column('resource_id', sa.Integer(), nullable=True, comment='关联资源ID'),
        sa.Column('description', sa.String(500), nullable=True, comment='权限描述'),
        sa.Column('status', sa.Integer(), nullable=True, server_default='1', comment='状态（0:禁用 1:启用）'),
        sa.Column('creation_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('created_by', sa.BigInteger(), nullable=True, comment='创建人ID'),
        sa.Column('updation_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('updated_by', sa.BigInteger(), nullable=True, comment='更新人ID'),
        sa.Column('enabled_flag', sa.Boolean(), nullable=False, server_default='1', comment='是否删除, 0 删除 1 非删除'),
        sa.Column('trace_id', sa.String(255), nullable=True, comment='trace_id'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        comment='权限表'
    )
    op.create_index('ix_sys_permission_permission_code', 'sys_permission', ['permission_code'], unique=True)
    
    # 创建关联表
    op.create_table(
        'sys_user_role',
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['sys_user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['sys_role.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    op.create_table(
        'sys_role_menu',
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.Column('menu_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['sys_role.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['menu_id'], ['sys_menu.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'menu_id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    op.create_table(
        'sys_role_dept',
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.Column('dept_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['sys_role.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dept_id'], ['sys_dept.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'dept_id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )


def downgrade() -> None:
    # 删除关联表
    op.drop_table('sys_role_dept')
    op.drop_table('sys_role_menu')
    op.drop_table('sys_user_role')
    
    # 删除主表
    op.drop_table('sys_permission')
    op.drop_table('sys_dict_data')
    op.drop_table('sys_dict_type')
    op.drop_table('sys_menu')
    op.drop_table('sys_dept')
    op.drop_table('sys_role')
    op.drop_table('sys_user')
