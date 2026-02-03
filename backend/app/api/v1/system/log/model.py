"""
日志数据模型
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, MetaData
from sqlalchemy.ext.declarative import declarative_base

# 创建独立的元数据和基类，避免与其他模型冲突
log_metadata = MetaData()
LogBase = declarative_base(metadata=log_metadata)


class OperationLogModel(LogBase):
    """操作日志模型"""
    
    __tablename__ = "sys_operation_log"
    __table_args__ = {'comment': '操作日志表'}
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    user_id = Column(Integer, nullable=True, comment="操作用户ID")
    username = Column(String(64), nullable=True, comment="操作用户名")
    operation = Column(String(100), nullable=False, comment="操作类型")
    method = Column(String(10), nullable=False, comment="请求方法")
    url = Column(String(500), nullable=False, comment="请求URL")
    ip = Column(String(50), nullable=True, comment="操作IP")
    location = Column(String(200), nullable=True, comment="操作地点")
    user_agent = Column(Text, nullable=True, comment="用户代理")
    
    module = Column(String(100), nullable=True, comment="操作模块")
    description = Column(String(500), nullable=True, comment="操作描述")
    request_data = Column(JSON, nullable=True, comment="请求参数")
    response_data = Column(JSON, nullable=True, comment="响应数据")
    
    status = Column(Integer, nullable=False, default=1, comment="操作状态（0:失败 1:成功）")
    error_msg = Column(Text, nullable=True, comment="错误信息")
    execution_time = Column(Integer, nullable=True, comment="执行时间(毫秒)")
    
    operation_time = Column(DateTime, nullable=False, comment="操作时间")
    creation_date = Column(DateTime, nullable=False, comment="创建时间")
    updation_date = Column(DateTime, nullable=False, comment="更新时间")
    created_by = Column(Integer, nullable=True, comment="创建人")
    updated_by = Column(Integer, nullable=True, comment="更新人")


class LoginLogModel(LogBase):
    """登录日志模型"""
    
    __tablename__ = "sys_login_log"
    __table_args__ = {'comment': '登录日志表'}
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    user_id = Column(Integer, nullable=True, comment="用户ID")
    username = Column(String(64), nullable=False, comment="用户名")
    login_type = Column(String(20), nullable=False, default="web", comment="登录类型")
    
    ip = Column(String(50), nullable=True, comment="登录IP")
    location = Column(String(200), nullable=True, comment="登录地点")
    user_agent = Column(Text, nullable=True, comment="用户代理")
    browser = Column(String(100), nullable=True, comment="浏览器")
    os = Column(String(100), nullable=True, comment="操作系统")
    
    status = Column(Integer, nullable=False, comment="登录状态（0:失败 1:成功）")
    message = Column(String(500), nullable=True, comment="登录信息")
    
    login_time = Column(DateTime, nullable=False, comment="登录时间")
    logout_time = Column(DateTime, nullable=True, comment="退出时间")
    creation_date = Column(DateTime, nullable=False, comment="创建时间")
    updation_date = Column(DateTime, nullable=False, comment="更新时间")
    created_by = Column(Integer, nullable=True, comment="创建人")
    updated_by = Column(Integer, nullable=True, comment="更新人")