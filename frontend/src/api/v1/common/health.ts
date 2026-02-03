import request from '/@/utils/request';

/**
 * 健康检查API - 新架构
 */
export function useHealthApi() {
  return {
    // 健康检查
    check: () => {
      return request({
        url: '/v1/common/health',
        method: 'GET',
      });
    },
    
    // 就绪检查
    readiness: () => {
      return request({
        url: '/v1/common/health/readiness',
        method: 'GET',
      });
    },
    
    // 存活检查
    liveness: () => {
      return request({
        url: '/v1/common/health/liveness',
        method: 'GET',
      });
    },
    
    // 获取系统信息
    info: () => {
      return request({
        url: '/v1/common/health/info',
        method: 'GET',
      });
    },
  };
}
