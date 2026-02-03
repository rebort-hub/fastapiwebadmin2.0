"""
数据字典数据模型
"""

from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base_model import BaseModel


class DictTypeModel(BaseModel):
    """字典类型模型"""
    
    __tablename__ = "sys_dict_type"
    __table_args__ = {'comment': '字典类型表'}
    
    dict_name = Column(String(100), nullable=False, comment="字典名称")
    dict_type = Column(String(100), nullable=False, unique=True, index=True, comment="字典类型")
    status = Column(Integer, nullable=True, default=1, comment="状态（0:禁用 1:启用）")
    remark = Column(String(500), nullable=True, comment="备注")
    
    # 关联字典数据
    dict_data = relationship(
        "DictDataModel",
        back_populates="dict_type_rel",
        cascade="all, delete-orphan",
        foreign_keys="DictDataModel.dict_type",
        primaryjoin="DictTypeModel.dict_type == foreign(DictDataModel.dict_type)",
        lazy="selectin"
    )


class DictDataModel(BaseModel):
    """字典数据模型"""
    
    __tablename__ = "sys_dict_data"
    __table_args__ = {'comment': '字典数据表'}
    
    dict_sort = Column(Integer, nullable=True, default=0, comment="字典排序")
    dict_label = Column(String(100), nullable=False, comment="字典标签")
    dict_value = Column(String(100), nullable=False, comment="字典键值")
    dict_type = Column(String(100), ForeignKey('sys_dict_type.dict_type'), nullable=False, index=True, comment="字典类型")
    css_class = Column(String(100), nullable=True, comment="样式属性（CSS类名）")
    list_class = Column(String(100), nullable=True, comment="表格回显样式")
    is_default = Column(Integer, nullable=True, default=0, comment="是否默认（0:否 1:是）")
    status = Column(Integer, nullable=True, default=1, comment="状态（0:禁用 1:启用）")
    remark = Column(String(500), nullable=True, comment="备注")
    
    # 关联字典类型
    dict_type_rel = relationship(
        "DictTypeModel",
        back_populates="dict_data",
        foreign_keys=[dict_type],
        lazy="selectin"
    )
