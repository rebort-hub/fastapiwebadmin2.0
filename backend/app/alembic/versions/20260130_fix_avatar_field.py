"""fix avatar field size

Revision ID: fix_avatar_001
Revises: init_menus_001
Create Date: 2026-01-30 16:40:00.000000

将user表的avatar字段从TEXT改为MEDIUMTEXT，支持更大的base64图片
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'fix_avatar_001'
down_revision = 'init_menus_001'
branch_labels = None
depends_on = None


def upgrade():
    """将avatar字段改为MEDIUMTEXT"""
    # MEDIUMTEXT可以存储最大16MB的数据，足够存储base64编码的图片
    op.alter_column('user', 'avatar',
                    existing_type=sa.Text(),
                    type_=mysql.MEDIUMTEXT(),
                    existing_nullable=False,
                    existing_comment='头像')


def downgrade():
    """回滚到TEXT类型"""
    op.alter_column('user', 'avatar',
                    existing_type=mysql.MEDIUMTEXT(),
                    type_=sa.Text(),
                    existing_nullable=False,
                    existing_comment='头像')
