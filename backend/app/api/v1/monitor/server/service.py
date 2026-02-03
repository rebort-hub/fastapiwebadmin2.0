"""
服务器监控服务
"""

import psutil
import platform
import socket
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.api.v1.monitor.server.model import (
    ServerInfo, CPUInfo, MemoryInfo, DiskInfo, 
    NetworkInfo, ProcessInfo, ServerMonitorData
)


class ServerMonitorService:
    """服务器监控服务"""
    
    @staticmethod
    def get_server_info() -> ServerInfo:
        """获取服务器基本信息"""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        return ServerInfo(
            hostname=socket.gethostname(),
            platform=platform.system(),
            architecture=platform.architecture()[0],
            processor=platform.processor() or "Unknown",
            boot_time=boot_time.strftime("%Y-%m-%d %H:%M:%S"),
            uptime=str(uptime).split('.')[0]  # 去掉微秒
        )
    
    @staticmethod
    def get_cpu_info() -> CPUInfo:
        """获取CPU信息"""
        cpu_freq = psutil.cpu_freq()
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
        
        return CPUInfo(
            physical_cores=psutil.cpu_count(logical=False),
            logical_cores=psutil.cpu_count(logical=True),
            current_frequency=round(cpu_freq.current, 2) if cpu_freq else 0.0,
            min_frequency=round(cpu_freq.min, 2) if cpu_freq else 0.0,
            max_frequency=round(cpu_freq.max, 2) if cpu_freq else 0.0,
            usage_percent=round(cpu_percent, 2),
            usage_per_core=[round(x, 2) for x in cpu_per_core]
        )
    
    @staticmethod
    def get_memory_info() -> MemoryInfo:
        """获取内存信息"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return MemoryInfo(
            total=memory.total,
            available=memory.available,
            used=memory.used,
            free=memory.free,
            usage_percent=round(memory.percent, 2),
            swap_total=swap.total,
            swap_used=swap.used,
            swap_free=swap.free,
            swap_percent=round(swap.percent, 2)
        )
    
    @staticmethod
    def get_disk_info() -> List[DiskInfo]:
        """获取磁盘信息"""
        disk_info = []
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append(DiskInfo(
                    device=partition.device,
                    mountpoint=partition.mountpoint,
                    fstype=partition.fstype,
                    total=partition_usage.total,
                    used=partition_usage.used,
                    free=partition_usage.free,
                    usage_percent=round(partition_usage.percent, 2)
                ))
            except PermissionError:
                # 某些系统分区可能没有权限访问
                continue
        
        return disk_info
    
    @staticmethod
    def get_network_info() -> List[NetworkInfo]:
        """获取网络信息"""
        network_info = []
        net_io = psutil.net_io_counters(pernic=True)
        
        for interface, stats in net_io.items():
            # 过滤掉回环接口和虚拟接口
            if interface.startswith(('lo', 'docker', 'veth')):
                continue
                
            network_info.append(NetworkInfo(
                interface=interface,
                bytes_sent=stats.bytes_sent,
                bytes_recv=stats.bytes_recv,
                packets_sent=stats.packets_sent,
                packets_recv=stats.packets_recv,
                errin=stats.errin,
                errout=stats.errout,
                dropin=stats.dropin,
                dropout=stats.dropout
            ))
        
        return network_info
    
    @staticmethod
    def get_top_processes(limit: int = 10) -> List[ProcessInfo]:
        """获取占用资源最多的进程"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 
                                       'cpu_percent', 'memory_percent', 
                                       'memory_info', 'create_time', 'cmdline']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] is None:
                    pinfo['cpu_percent'] = 0.0
                if pinfo['memory_percent'] is None:
                    pinfo['memory_percent'] = 0.0
                
                create_time = datetime.fromtimestamp(pinfo['create_time'])
                cmdline = ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else ''
                
                processes.append(ProcessInfo(
                    pid=pinfo['pid'],
                    name=pinfo['name'] or 'Unknown',
                    username=pinfo['username'] or 'Unknown',
                    status=pinfo['status'],
                    cpu_percent=round(pinfo['cpu_percent'], 2),
                    memory_percent=round(pinfo['memory_percent'], 2),
                    memory_info=pinfo['memory_info'].rss if pinfo['memory_info'] else 0,
                    create_time=create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    cmdline=cmdline[:100] + '...' if len(cmdline) > 100 else cmdline
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # 按CPU使用率排序，取前N个
        processes.sort(key=lambda x: x.cpu_percent, reverse=True)
        return processes[:limit]
    
    @classmethod
    def get_monitor_data(cls) -> ServerMonitorData:
        """获取完整的服务器监控数据"""
        return ServerMonitorData(
            server_info=cls.get_server_info(),
            cpu_info=cls.get_cpu_info(),
            memory_info=cls.get_memory_info(),
            disk_info=cls.get_disk_info(),
            network_info=cls.get_network_info(),
            top_processes=cls.get_top_processes(),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        """格式化字节数为可读格式"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"