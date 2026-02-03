"""fix user status values

Revision ID: fix_user_status_001
Revises: avatar_nullable_001
Create Date: 2026-01-30 16:50:00.000000

修复用户状态值的定义：
- 旧定义：0=正常，1=锁定
- 新定义：1=启用，0=禁用
需要反转所有现有用户的status值
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_user_status_001'
down_revision = 'avatar_nullable_001'
branch_labels = None
depends_on = None


def upgrade():
    """反转用户status值：0→1, 1→0"""
    conn = op.get_bind()
    
    # 使用临时值2来避免冲突
    # 步骤1：0 → 2
    conn.execute(sa.text("UPDATE user SET status = 2 WHERE status = 0"))
    # 步骤2：1 → 0
    conn.execute(sa.text("UPDATE user SET status = 0 WHERE status = 1"))
    # 步骤3：2 → 1
    conn.execute(sa.text("UPDATE user SET status = 1 WHERE status = 2"))


def downgrade():
    """回滚：反转回原来的值"""
    conn = op.get_bind()
    
    # 使用临时值2来避免冲突
    # 步骤1：1 → 2
    conn.execute(sa.text("UPDATE user SET status = 2 WHERE status = 1"))
    # 步骤2：0 → 1
    conn.execute(sa.text("UPDATE user SET status = 1 WHERE status = 0"))
    # 步骤3：2 → 0
    conn.execute(sa.text("UPDATE user SET status = 0 WHERE status = 2"))
