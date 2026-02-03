"""
基础数据模型
提供通用字段和方法
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declared_attr
from app.db.sqlalchemy import Base


class TimestampMixin:
    """时间戳Mixin"""
    
    @declared_attr
    def created_at(cls):
        """创建时间"""
        return Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    
    @declared_attr
    def updated_at(cls):
        """更新时间"""
        return Column(
            DateTime,
            default=datetime.now,
            onupdate=datetime.now,
            nullable=False,
            comment="更新时间"
        )


class AuditMixin:
    """审计字段Mixin"""
    
    @declared_attr
    def created_by(cls):
        """创建人ID"""
        return Column(Integer, nullable=True, comment="创建人ID")
    
    @declared_attr
    def updated_by(cls):
        """更新人ID"""
        return Column(Integer, nullable=True, comment="更新人ID")


class BaseModel(Base, TimestampMixin, AuditMixin):
    """基础模型类"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    
    def to_dict(self):
        """转换为字典"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
