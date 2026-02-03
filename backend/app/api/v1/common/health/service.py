"""
健康检查业务逻辑层
"""

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    
import platform
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class HealthService:
    """健康检查服务"""
    
    @classmethod
    async def basic_health_check_service(cls) -> dict:
        """基础健康检查"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    
    @classmethod
    async def database_health_check_service(cls, db: AsyncSession) -> dict:
        """数据库健康检查"""
        try:
            # 执行简单查询测试连接
            result = await db.execute(text("SELECT 1"))
            result.scalar()
            
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @classmethod
    async def get_system_info_service(cls) -> dict:
        """获取系统信息"""
        
        if not PSUTIL_AVAILABLE:
            return {
                "system": {
                    "platform": platform.system(),
                    "platform_release": platform.release(),
                    "platform_version": platform.version(),
                    "architecture": platform.machine(),
                    "hostname": platform.node(),
                    "python_version": platform.python_version()
                },
                "note": "psutil not installed, system metrics unavailable",
                "timestamp": datetime.now().isoformat()
            }
        
        # CPU信息
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # 内存信息
        memory = psutil.virtual_memory()
        memory_total = round(memory.total / (1024 ** 3), 2)  # GB
        memory_used = round(memory.used / (1024 ** 3), 2)  # GB
        memory_percent = memory.percent
        
        # 磁盘信息
        disk = psutil.disk_usage('/')
        disk_total = round(disk.total / (1024 ** 3), 2)  # GB
        disk_used = round(disk.used / (1024 ** 3), 2)  # GB
        disk_percent = disk.percent
        
        return {
            "system": {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "hostname": platform.node(),
                "python_version": platform.python_version()
            },
            "cpu": {
                "count": cpu_count,
                "percent": cpu_percent
            },
            "memory": {
                "total_gb": memory_total,
                "used_gb": memory_used,
                "percent": memory_percent
            },
            "disk": {
                "total_gb": disk_total,
                "used_gb": disk_used,
                "percent": disk_percent
            },
            "timestamp": datetime.now().isoformat()
        }
