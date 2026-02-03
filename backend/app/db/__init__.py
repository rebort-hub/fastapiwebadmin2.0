# -*- coding: utf-8 -*-
# @author: rebort

# 延迟导入Redis，避免在不需要时导入
redis_pool = None

def get_redis_pool():
    """获取Redis连接池（延迟初始化）"""
    global redis_pool
    if redis_pool is None:
        from app.db.redis import RedisPool
        from config import config
        redis_pool = RedisPool()
    return redis_pool
