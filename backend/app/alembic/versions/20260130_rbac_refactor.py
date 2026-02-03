"""RBAC standard refactor

Revision ID: rbac_refactor_001
Revises: d45d346a66e1
Create Date: 2026-01-30 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'rbac_refactor_001'
down_revision = 'd45d346a66e1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """升级到标准 RBAC 设计"""
    
    # 1. 创建权限表
    op.create_table('permission',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
        sa.Column('permission_code', sa.String(length=100), nullable=False, comment='权限编码 如: user:add'),
        sa.Column('permission_name', sa.String(length=100), nullable=False, comment='权限名称'),
        sa.Column('permission_type', sa.SmallInteger(), nullable=False, comment='1菜单权限 2按钮权限 3数据权限 4API权限'),
        sa.Column('resource_type', sa.String(length=50), nullable=True, comment='资源类型'),
        sa.Column('resource_id', sa.BigInteger(), nullable=True, comment='关联资源ID'),
        sa.Column('status', sa.SmallInteger(), nullable=True, default=1, comment='1启用 0禁用'),
        sa.Column('sort', sa.Integer(), nullable=True, default=0, comment='排序'),
        sa.Column('description', sa.String(length=500), nullable=True, comment='描述'),
        sa.Column('creation_date', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('created_by', sa.BigInteger(), nullable=True, comment='创建人ID'),
        sa.Column('updation_date', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.Column('updated_by', sa.BigInteger(), nullable=True, comment='更新人ID'),
        sa.Column('enabled_flag', sa.Boolean(), nullable=False, default=True, comment='是否删除, 0 删除 1 非删除'),
        sa.Column('trace_id', sa.String(length=64), nullable=True, comment='trace_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('permission_code', name='uk_permission_code'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('idx_permission_code', 'permission', ['permission_code'])
    op.create_index('idx_permission_type', 'permission', ['permission_type'])
    op.create_index('idx_resource', 'permission', ['resource_type', 'resource_id'])
    
    # 2. 创建用户-角色关联表
    op.create_table('user_role',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='用户ID'),
        sa.Column('role_id', sa.BigInteger(), nullable=False, comment='角色ID'),
        sa.Column('creation_date', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('created_by', sa.BigInteger(), nullable=True, comment='创建人ID'),
        sa.Column('updation_date', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.Column('updated_by', sa.BigInteger(), nullable=True, comment='更新人ID'),
        sa.Column('enabled_flag', sa.Boolean(), nullable=False, default=True, comment='是否删除'),
        sa.Column('trace_id', sa.String(length=64), nullable=True, comment='trace_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'role_id', name='uk_user_role'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('idx_user_id', 'user_role', ['user_id'])
    op.create_index('idx_role_id', 'user_role', ['role_id'])
    
    # 3. 创建角色-菜单关联表
    op.create_table('role_menu',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
        sa.Column('role_id', sa.BigInteger(), nullable=False, comment='角色ID'),
        sa.Column('menu_id', sa.BigInteger(), nullable=False, comment='菜单ID'),
        sa.Column('creation_date', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('created_by', sa.BigInteger(), nullable=True, comment='创建人ID'),
        sa.Column('updation_date', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.Column('updated_by', sa.BigInteger(), nullable=True, comment='更新人ID'),
        sa.Column('enabled_flag', sa.Boolean(), nullable=False, default=True, comment='是否删除'),
        sa.Column('trace_id', sa.String(length=64), nullable=True, comment='trace_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'menu_id', name='uk_role_menu'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('idx_role_id_rm', 'role_menu', ['role_id'])
    op.create_index('idx_menu_id', 'role_menu', ['menu_id'])
    
    # 4. 创建角色-权限关联表
    op.create_table('role_permission',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
        sa.Column('role_id', sa.BigInteger(), nullable=False, comment='角色ID'),
        sa.Column('permission_id', sa.BigInteger(), nullable=False, comment='权限ID'),
        sa.Column('creation_date', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('created_by', sa.BigInteger(), nullable=True, comment='创建人ID'),
        sa.Column('updation_date', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.Column('updated_by', sa.BigInteger(), nullable=True, comment='更新人ID'),
        sa.Column('enabled_flag', sa.Boolean(), nullable=False, default=True, comment='是否删除'),
        sa.Column('trace_id', sa.String(length=64), nullable=True, comment='trace_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'permission_id', name='uk_role_permission'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('idx_role_id_rp', 'role_permission', ['role_id'])
    op.create_index('idx_permission_id', 'role_permission', ['permission_id'])
    
    # 5. 修改 roles 表
    # 添加新字段
    op.add_column('roles', sa.Column('role_code', sa.String(length=64), nullable=True, comment='角色编码'))
    op.add_column('roles', sa.Column('data_scope', sa.SmallInteger(), nullable=True, default=1, 
                                     comment='数据权限范围 1全部 2本部门 3本部门及下级 4仅本人'))
    op.add_column('roles', sa.Column('sort', sa.Integer(), nullable=True, default=0, comment='排序'))
    
    # 修改字段类型和注释
    op.alter_column('roles', 'menus',
                   existing_type=sa.String(64),
                   type_=sa.Text(),
                   comment='菜单列表（逗号分隔，待迁移后删除）',
                   existing_nullable=True)
    
    # 创建索引
    op.create_index('idx_role_code', 'roles', ['role_code'])
    
    # 6. 修改 menu 表
    # 添加权限标识字段
    op.add_column('menu', sa.Column('permission', sa.String(length=100), nullable=True, comment='权限标识'))
    op.add_column('menu', sa.Column('visible', sa.SmallInteger(), nullable=True, default=1, comment='1显示 0隐藏'))
    
    # 修改 menu_type 注释
    op.alter_column('menu', 'menu_type',
                   existing_type=sa.Integer(),
                   comment='菜单类型 1目录 2菜单 3按钮',
                   existing_nullable=True)
    
    # 创建权限标识索引
    op.create_index('idx_permission', 'menu', ['permission'])
    
    # 7. 修改 department 表
    op.add_column('department', sa.Column('dept_code', sa.String(length=64), nullable=True, comment='部门编码'))
    op.add_column('department', sa.Column('ancestors', sa.String(length=500), nullable=True, comment='祖级列表'))
    op.add_column('department', sa.Column('leader_id', sa.BigInteger(), nullable=True, comment='负责人ID'))
    op.add_column('department', sa.Column('phone', sa.String(length=20), nullable=True, comment='联系电话'))
    op.add_column('department', sa.Column('email', sa.String(length=100), nullable=True, comment='邮箱'))
    
    op.create_index('idx_dept_code', 'department', ['dept_code'])
    
    # 8. 修改 user 表
    op.add_column('user', sa.Column('phone', sa.String(length=20), nullable=True, comment='手机号'))
    op.add_column('user', sa.Column('last_login_time', sa.DateTime(), nullable=True, comment='最后登录时间'))
    op.add_column('user', sa.Column('last_login_ip', sa.String(length=50), nullable=True, comment='最后登录IP'))
    
    # 修改 roles 字段注释（保留用于数据迁移）
    op.alter_column('user', 'roles',
                   existing_type=mysql.JSON(),
                   comment='用户角色（JSON数组，待迁移后删除）',
                   existing_nullable=False)


def downgrade() -> None:
    """回滚到旧设计"""
    
    # 删除 user 表新增字段
    op.drop_column('user', 'last_login_ip')
    op.drop_column('user', 'last_login_time')
    op.drop_column('user', 'phone')
    
    # 删除 department 表新增字段
    op.drop_index('idx_dept_code', table_name='department')
    op.drop_column('department', 'email')
    op.drop_column('department', 'phone')
    op.drop_column('department', 'leader_id')
    op.drop_column('department', 'ancestors')
    op.drop_column('department', 'dept_code')
    
    # 删除 menu 表新增字段和索引
    op.drop_index('idx_permission', table_name='menu')
    op.drop_column('menu', 'visible')
    op.drop_column('menu', 'permission')
    
    # 删除 roles 表新增字段和索引
    op.drop_index('idx_role_code', table_name='roles')
    op.drop_column('roles', 'sort')
    op.drop_column('roles', 'data_scope')
    op.drop_column('roles', 'role_code')
    
    # 删除关联表
    op.drop_index('idx_permission_id', table_name='role_permission')
    op.drop_index('idx_role_id_rp', table_name='role_permission')
    op.drop_table('role_permission')
    
    op.drop_index('idx_menu_id', table_name='role_menu')
    op.drop_index('idx_role_id_rm', table_name='role_menu')
    op.drop_table('role_menu')
    
    op.drop_index('idx_role_id', table_name='user_role')
    op.drop_index('idx_user_id', table_name='user_role')
    op.drop_table('user_role')
    
    op.drop_index('idx_resource', table_name='permission')
    op.drop_index('idx_permission_type', table_name='permission')
    op.drop_index('idx_permission_code', table_name='permission')
    op.drop_table('permission')
