"""
服务器监控控制器
"""

from fastapi import APIRouter, Depends
from app.common.response import success_response
from app.api.v1.monitor.server.service import ServerMonitorService
from app.api.v1.system.auth.dependencies import get_current_user
from app.models.system_models import User

router = APIRouter()


@router.get("/info", summary="获取服务器监控信息")
async def get_server_monitor_info(current_user: User = Depends(get_current_user)):
    """
    获取服务器监控信息
    """
    monitor_data = ServerMonitorService.get_monitor_data()
    return success_response(data=monitor_data.dict())


@router.get("/cpu", summary="获取CPU信息")
async def get_cpu_info(current_user: User = Depends(get_current_user)):
    """
    获取CPU信息
    """
    cpu_info = ServerMonitorService.get_cpu_info()
    return success_response(data=cpu_info.dict())


@router.get("/memory", summary="获取内存信息")
async def get_memory_info(current_user: User = Depends(get_current_user)):
    """
    获取内存信息
    """
    memory_info = ServerMonitorService.get_memory_info()
    return success_response(data=memory_info.dict())


@router.get("/disk", summary="获取磁盘信息")
async def get_disk_info(current_user: User = Depends(get_current_user)):
    """
    获取磁盘信息
    """
    disk_info = ServerMonitorService.get_disk_info()
    return success_response(data=[disk.dict() for disk in disk_info])


@router.get("/network", summary="获取网络信息")
async def get_network_info(current_user: User = Depends(get_current_user)):
    """
    获取网络信息
    """
    network_info = ServerMonitorService.get_network_info()
    return success_response(data=[net.dict() for net in network_info])


@router.get("/processes", summary="获取进程信息")
async def get_processes_info(
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """
    获取占用资源最多的进程信息
    """
    processes = ServerMonitorService.get_top_processes(limit)
    return success_response(data=[proc.dict() for proc in processes])