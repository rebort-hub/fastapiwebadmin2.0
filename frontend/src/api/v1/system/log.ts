import request from '/@/utils/request';

/**
 * 日志管理API - 新架构
 */
export function useLogApi() {
  return {
    // 获取登录日志列表
    getLoginLogs: (params?: {
      page?: number;
      page_size?: number;
      username?: string;
      ip?: string;
      status?: number;
      begin_time?: string;
      end_time?: string;
    }) => {
      return request({
        url: '/v1/system/log/login',
        method: 'GET',
        params,
      });
    },
    
    // 获取操作日志列表
    getOperationLogs: (params?: {
      page?: number;
      page_size?: number;
      username?: string;
      operation?: string;
      method?: string;
      module?: string;
      status?: number;
      ip?: string;
      begin_time?: string;
      end_time?: string;
    }) => {
      return request({
        url: '/v1/system/log/operation',
        method: 'GET',
        params,
      });
    },
    
    // 获取日志详情
    getDetail: (id: number, type: 'login' | 'operation') => {
      return request({
        url: `/v1/system/log/${type}/${id}`,
        method: 'GET',
      });
    },
    
    // 删除登录日志
    deleteLoginLog: (id: number) => {
      return request({
        url: `/v1/system/log/login/${id}`,
        method: 'DELETE',
      });
    },
    
    // 批量删除登录日志
    batchDeleteLoginLogs: (ids: number[]) => {
      return request({
        url: '/v1/system/log/login',
        method: 'DELETE',
        data: { ids },
      });
    },
    
    // 清空登录日志
    clearLoginLogs: (days?: number) => {
      return request({
        url: '/v1/system/log/login/clean',
        method: 'DELETE',
        params: days ? { days } : undefined,
      });
    },
    
    // 删除操作日志
    deleteOperationLog: (id: number) => {
      return request({
        url: `/v1/system/log/operation/${id}`,
        method: 'DELETE',
      });
    },
    
    // 批量删除操作日志
    batchDeleteOperationLogs: (ids: number[]) => {
      return request({
        url: '/v1/system/log/operation',
        method: 'DELETE',
        data: { ids },
      });
    },
    
    // 清空操作日志
    clearOperationLogs: (days?: number) => {
      return request({
        url: '/v1/system/log/operation/clean',
        method: 'DELETE',
        params: days ? { days } : undefined,
      });
    },
    
    // 获取登录日志统计
    getLoginLogStatistics: () => {
      return request({
        url: '/v1/system/log/login/statistics',
        method: 'GET',
      });
    },
    
    // 获取操作日志统计
    getOperationLogStatistics: () => {
      return request({
        url: '/v1/system/log/operation/statistics',
        method: 'GET',
      });
    },
    
    // 兼容旧API：获取登录日志列表
    getList: (data?: any) => {
      return request({
        url: '/v1/system/log/login',
        method: 'GET',
        params: data,
      });
    },
    
    // 兼容旧API：删除登录日志
    deleted: (data?: any) => {
      if (data?.id) {
        return request({
          url: `/v1/system/log/login/${data.id}`,
          method: 'DELETE',
        });
      }
      throw new Error('缺少日志ID');
    },
  };
}
