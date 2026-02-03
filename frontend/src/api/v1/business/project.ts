import request from '/@/utils/request';

/**
 * 项目管理API
 * 注意：这是业务特定功能，待后续重构到新架构
 */
export function useProjectApi() {
  return {
    // 获取项目列表
    getList: (data?: any) => {
      return request({
        url: '/project/list',
        method: 'POST',
        data,
      });
    },
    
    // 保存或更新项目
    saveOrUpdate: (data?: any) => {
      return request({
        url: '/project/saveOrUpdate',
        method: 'POST',
        data,
      });
    },
    
    // 删除项目
    deleted: (data?: any) => {
      return request({
        url: '/project/deleted',
        method: 'POST',
        data,
      });
    },
  };
}
