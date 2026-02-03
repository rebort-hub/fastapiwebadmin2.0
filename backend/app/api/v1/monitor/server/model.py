"""
服务器监控数据模型
"""

from typing import Dict, Any
from pydantic import BaseModel


class ServerInfo(BaseModel):
    """服务器基本信息"""
    hostname: str
    platform: str
    architecture: str
    processor: str
    boot_time: str
    uptime: str


class CPUInfo(BaseModel):
    """CPU信息"""
    physical_cores: int
    logical_cores: int
    current_frequency: float
    min_frequency: float
    max_frequency: float
    usage_percent: float
    usage_per_core: list[float]


class MemoryInfo(BaseModel):
    """内存信息"""
    total: int
    available: int
    used: int
    free: int
    usage_percent: float
    swap_total: int
    swap_used: int
    swap_free: int
    swap_percent: float


class DiskInfo(BaseModel):
    """磁盘信息"""
    device: str
    mountpoint: str
    fstype: str
    total: int
    used: int
    free: int
    usage_percent: float


class NetworkInfo(BaseModel):
    """网络信息"""
    interface: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int


class ProcessInfo(BaseModel):
    """进程信息"""
    pid: int
    name: str
    username: str
    status: str
    cpu_percent: float
    memory_percent: float
    memory_info: int
    create_time: str
    cmdline: str


class ServerMonitorData(BaseModel):
    """服务器监控数据"""
    server_info: ServerInfo
    cpu_info: CPUInfo
    memory_info: MemoryInfo
    disk_info: list[DiskInfo]
    network_info: list[NetworkInfo]
    top_processes: list[ProcessInfo]
    timestamp: str