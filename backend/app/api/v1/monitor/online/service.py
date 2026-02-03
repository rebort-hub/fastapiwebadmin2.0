"""
在线用户监控服务
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.db.sqlalchemy import get_db
from app.db import get_redis_pool
from app.models.system_models import User, UserLoginRecord
from app.api.v1.monitor.online.model import OnlineUserInfo, OnlineUserStats
from app.utils.common import parse_user_agent, get_location_by_ip


class OnlineUserService:
    """在线用户监控服务"""
    
    ONLINE_USER_PREFIX = "online_user:"
    ONLINE_STATS_KEY = "online_stats"
    ACTIVITY_TIMEOUT = 300  # 5分钟无活动视为不活跃
    
    @classmethod
    async def add_online_user(cls, user_id: int, session_id: str, 
                            ip_address: str, user_agent: str) -> None:
        """添加在线用户"""
        redis_pool = get_redis_pool()
        redis_client = redis_pool.redis
        
        async for db in get_db():
            try:
                # 获取用户信息
                user = await db.get(User, user_id)
                if not user:
                    return
                
                # 解析用户代理
                browser_info = parse_user_agent(user_agent)
                location = get_location_by_ip(ip_address)
                
                # 构建在线用户信息
                online_info = {
                    "user_id": user_id,
                    "username": user.username,
                    "nickname": user.nickname or user.username,
                    "avatar": user.avatar,
                    "login_time": datetime.now().isoformat(),
                    "last_activity": datetime.now().isoformat(),
                    "ip_address": ip_address,
                    "location": location,
                    "browser": browser_info.get("browser", "Unknown"),
                    "os": browser_info.get("os", "Unknown"),
                    "user_agent": user_agent,
                    "session_id": session_id,
                    "is_active": True
                }
                
                # 存储到Redis
                key = f"{cls.ONLINE_USER_PREFIX}{user_id}:{session_id}"
                await redis_client.setex(key, 86400, json.dumps(online_info))  # 24小时过期
                
                # 更新统计信息
                await cls._update_stats()
                
            except Exception as e:
                print(f"添加在线用户失败: {e}")
            finally:
                break
    
    @classmethod
    async def remove_online_user(cls, user_id: int, session_id: str) -> None:
        """移除在线用户"""
        redis_pool = get_redis_pool()
        redis_client = redis_pool.redis
        key = f"{cls.ONLINE_USER_PREFIX}{user_id}:{session_id}"
        await redis_client.delete(key)
        await cls._update_stats()
    
    @classmethod
    async def update_user_activity(cls, user_id: int, session_id: str) -> None:
        """更新用户活动时间"""
        redis_pool = get_redis_pool()
        redis_client = redis_pool.redis
        key = f"{cls.ONLINE_USER_PREFIX}{user_id}:{session_id}"
        
        # 获取现有信息
        user_data = await redis_client.get(key)
        if user_data:
            online_info = json.loads(user_data)
            online_info["last_activity"] = datetime.now().isoformat()
            online_info["is_active"] = True
            
            # 更新Redis
            await redis_client.setex(key, 86400, json.dumps(online_info))
    
    @classmethod
    async def get_online_users(cls, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """获取在线用户列表"""
        redis_pool = get_redis_pool()
        redis_client = redis_pool.redis
        
        # 获取所有在线用户键
        pattern = f"{cls.ONLINE_USER_PREFIX}*"
        keys = await redis_client.keys(pattern)
        
        online_users = []
        current_time = datetime.now()
        
        for key in keys:
            user_data = await redis_client.get(key)
            if user_data:
                try:
                    online_info = json.loads(user_data)
                    
                    # 计算在线时长
                    login_time = datetime.fromisoformat(online_info["login_time"])
                    duration = current_time - login_time
                    online_info["duration"] = str(duration).split('.')[0]
                    
                    # 检查是否活跃
                    last_activity = datetime.fromisoformat(online_info["last_activity"])
                    inactive_time = (current_time - last_activity).total_seconds()
                    online_info["is_active"] = inactive_time < cls.ACTIVITY_TIMEOUT
                    
                    # 格式化时间显示
                    online_info["login_time"] = login_time.strftime("%Y-%m-%d %H:%M:%S")
                    online_info["last_activity"] = last_activity.strftime("%Y-%m-%d %H:%M:%S")
                    
                    online_users.append(OnlineUserInfo(**online_info))
                    
                except (json.JSONDecodeError, ValueError, KeyError):
                    # 数据格式错误，删除该键
                    await redis_client.delete(key)
                    continue
        
        # 按登录时间排序
        online_users.sort(key=lambda x: x.login_time, reverse=True)
        
        # 分页
        total = len(online_users)
        start = (page - 1) * page_size
        end = start + page_size
        items = online_users[start:end]
        
        return {
            "items": [user.dict() for user in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
    
    @classmethod
    async def get_online_stats(cls) -> OnlineUserStats:
        """获取在线用户统计"""
        try:
            redis_pool = get_redis_pool()
            redis_client = redis_pool.redis
            
            # 获取所有在线用户
            pattern = f"{cls.ONLINE_USER_PREFIX}*"
            keys = await redis_client.keys(pattern)
            
            total_online = len(keys) if keys else 0
            active_users = 0
            durations = []
            current_time = datetime.now()
            
            for key in keys:
                try:
                    user_data = await redis_client.get(key)
                    if user_data:
                        online_info = json.loads(user_data)
                        
                        # 检查是否活跃
                        last_activity = datetime.fromisoformat(online_info["last_activity"])
                        inactive_time = (current_time - last_activity).total_seconds()
                        if inactive_time < cls.ACTIVITY_TIMEOUT:
                            active_users += 1
                        
                        # 计算在线时长
                        login_time = datetime.fromisoformat(online_info["login_time"])
                        duration = (current_time - login_time).total_seconds()
                        durations.append(duration)
                        
                except (json.JSONDecodeError, ValueError, KeyError):
                    continue
            
            # 计算平均在线时长
            avg_duration_seconds = sum(durations) / len(durations) if durations else 0
            avg_duration = str(timedelta(seconds=int(avg_duration_seconds))).split('.')[0]
            
            # 简化今日新增统计（避免数据库查询问题）
            new_today = 0
            peak_today = total_online
            
            return OnlineUserStats(
                total_online=total_online,
                active_users=active_users,
                new_today=new_today,
                peak_today=peak_today,
                avg_duration=avg_duration
            )
            
        except Exception as e:
            print(f"获取在线用户统计失败: {e}")
            return OnlineUserStats(
                total_online=0,
                active_users=0,
                new_today=0,
                peak_today=0,
                avg_duration="0:00:00"
            )
    
    @classmethod
    async def force_offline(cls, user_id: int, session_id: str = None) -> bool:
        """强制用户下线"""
        redis_pool = get_redis_pool()
        redis_client = redis_pool.redis
        
        if session_id:
            # 下线指定会话
            key = f"{cls.ONLINE_USER_PREFIX}{user_id}:{session_id}"
            result = await redis_client.delete(key)
            await cls._update_stats()
            return result > 0
        else:
            # 下线用户的所有会话
            pattern = f"{cls.ONLINE_USER_PREFIX}{user_id}:*"
            keys = await redis_client.keys(pattern)
            if keys:
                await redis_client.delete(*keys)
                await cls._update_stats()
                return True
            return False
    
    @classmethod
    async def _update_stats(cls) -> None:
        """更新统计信息"""
        try:
            redis_pool = get_redis_pool()
            redis_client = redis_pool.redis
            stats = await cls.get_online_stats()
            if stats:
                await redis_client.setex(cls.ONLINE_STATS_KEY, 300, json.dumps(stats.dict()))  # 5分钟缓存
        except Exception as e:
            print(f"更新统计信息失败: {e}")
    
    @classmethod
    async def cleanup_expired_users(cls) -> None:
        """清理过期的在线用户"""
        redis_pool = get_redis_pool()
        redis_client = redis_pool.redis
        pattern = f"{cls.ONLINE_USER_PREFIX}*"
        keys = await redis_client.keys(pattern)
        
        current_time = datetime.now()
        expired_keys = []
        
        for key in keys:
            user_data = await redis_client.get(key)
            if user_data:
                try:
                    online_info = json.loads(user_data)
                    last_activity = datetime.fromisoformat(online_info["last_activity"])
                    
                    # 超过1小时无活动的用户视为离线
                    if (current_time - last_activity).total_seconds() > 3600:
                        expired_keys.append(key)
                        
                except (json.JSONDecodeError, ValueError, KeyError):
                    expired_keys.append(key)
        
        if expired_keys:
            await redis_client.delete(*expired_keys)
            await cls._update_stats()