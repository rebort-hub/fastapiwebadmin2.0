/**
 * 服务器监控API
 */

import request from '/@/utils/request';

export interface ServerInfo {
  hostname: string;
  platform: string;
  architecture: string;
  processor: string;
  boot_time: string;
  uptime: string;
}

export interface CPUInfo {
  physical_cores: number;
  logical_cores: number;
  current_frequency: number;
  min_frequency: number;
  max_frequency: number;
  usage_percent: number;
  usage_per_core: number[];
}

export interface MemoryInfo {
  total: number;
  available: number;
  used: number;
  free: number;
  usage_percent: number;
  swap_total: number;
  swap_used: number;
  swap_free: number;
  swap_percent: number;
}

export interface DiskInfo {
  device: string;
  mountpoint: string;
  fstype: string;
  total: number;
  used: number;
  free: number;
  usage_percent: number;
}

export interface NetworkInfo {
  interface: string;
  bytes_sent: number;
  bytes_recv: number;
  packets_sent: number;
  packets_recv: number;
  errin: number;
  errout: number;
  dropin: number;
  dropout: number;
}

export interface ProcessInfo {
  pid: number;
  name: string;
  username: string;
  status: string;
  cpu_percent: number;
  memory_percent: number;
  memory_info: number;
  create_time: string;
  cmdline: string;
}

export interface ServerMonitorData {
  server_info: ServerInfo;
  cpu_info: CPUInfo;
  memory_info: MemoryInfo;
  disk_info: DiskInfo[];
  network_info: NetworkInfo[];
  top_processes: ProcessInfo[];
  timestamp: string;
}

/**
 * 服务器监控API类
 */
export function useServerMonitorApi() {
  return {
    /**
     * 获取服务器监控信息
     */
    getServerInfo: (): Promise<IApiResponseData<ServerMonitorData>> => {
      return request({
        url: '/v1/monitor/server/info',
        method: 'get',
      });
    },

    /**
     * 获取CPU信息
     */
    getCPUInfo: (): Promise<IApiResponseData<CPUInfo>> => {
      return request({
        url: '/v1/monitor/server/cpu',
        method: 'get',
      });
    },

    /**
     * 获取内存信息
     */
    getMemoryInfo: (): Promise<IApiResponseData<MemoryInfo>> => {
      return request({
        url: '/v1/monitor/server/memory',
        method: 'get',
      });
    },

    /**
     * 获取磁盘信息
     */
    getDiskInfo: (): Promise<IApiResponseData<DiskInfo[]>> => {
      return request({
        url: '/v1/monitor/server/disk',
        method: 'get',
      });
    },

    /**
     * 获取网络信息
     */
    getNetworkInfo: (): Promise<IApiResponseData<NetworkInfo[]>> => {
      return request({
        url: '/v1/monitor/server/network',
        method: 'get',
      });
    },

    /**
     * 获取进程信息
     */
    getProcessInfo: (limit: number = 10): Promise<IApiResponseData<ProcessInfo[]>> => {
      return request({
        url: '/v1/monitor/server/processes',
        method: 'get',
        params: { limit },
      });
    },
  };
}