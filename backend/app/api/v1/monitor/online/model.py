"""
在线用户监控数据模型
"""

from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class OnlineUserInfo(BaseModel):
    """在线用户信息"""
    user_id: int
    username: str
    nickname: str
    avatar: Optional[str] = None
    login_time: str
    last_activity: str
    ip_address: str
    location: str
    browser: str
    os: str
    user_agent: str
    session_id: str
    is_active: bool = True
    duration: str  # 在线时长


class OnlineUserStats(BaseModel):
    """在线用户统计"""
    total_online: int
    active_users: int  # 活跃用户（最近5分钟有活动）
    new_today: int     # 今日新增登录
    peak_today: int    # 今日峰值
    avg_duration: str  # 平均在线时长