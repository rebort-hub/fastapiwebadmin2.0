"""make avatar nullable

Revision ID: avatar_nullable_001
Revises: fix_avatar_001
Create Date: 2026-01-30 16:45:00.000000

将user表的avatar字段改为可空，并设置默认值为空字符串
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'avatar_nullable_001'
down_revision = 'fix_avatar_001'
branch_labels = None
depends_on = None


def upgrade():
    """将avatar字段改为可空"""
    # TEXT类型不能有默认值，只能设置为可空
    op.alter_column('user', 'avatar',
                    existing_type=mysql.MEDIUMTEXT(),
                    nullable=True,
                    existing_comment='头像')


def downgrade():
    """回滚到不可空"""
    op.alter_column('user', 'avatar',
                    existing_type=mysql.MEDIUMTEXT(),
                    nullable=False,
                    existing_comment='头像')
