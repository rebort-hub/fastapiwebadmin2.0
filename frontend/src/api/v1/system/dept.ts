import request from '/@/utils/request';

/**
 * 部门管理API - 新架构
 */
export function useDeptApi() {
  return {
    // 获取部门列表
    getList: (params?: {
      name?: string;
      status?: number;
    }) => {
      return request({
        url: '/v1/system/dept',
        method: 'GET',
        params,
      });
    },
    
    // 获取部门树
    getTree: (params?: {
      status?: number;
    }) => {
      return request({
        url: '/v1/system/dept/tree',
        method: 'GET',
        params,
      });
    },
    
    // 获取部门详情
    getDetail: (id: number) => {
      return request({
        url: `/v1/system/dept/${id}`,
        method: 'GET',
      });
    },
    
    // 创建部门
    create: (data: any) => {
      return request({
        url: '/v1/system/dept',
        method: 'POST',
        data,
      });
    },
    
    // 更新部门
    update: (id: number, data: any) => {
      return request({
        url: `/v1/system/dept/${id}`,
        method: 'PUT',
        data,
      });
    },
    
    // 删除部门
    delete: (id: number) => {
      return request({
        url: `/v1/system/dept/${id}`,
        method: 'DELETE',
      });
    },
    
    // 更新部门状态
    updateStatus: (id: number, status: number) => {
      return request({
        url: `/v1/system/dept/${id}/status`,
        method: 'PUT',
        data: { status },
      });
    },
    
    // 更新部门排序
    updateSort: (id: number, sort: number) => {
      return request({
        url: `/v1/system/dept/${id}/sort`,
        method: 'PUT',
        data: { sort },
      });
    },
    
    // 获取部门下的用户
    getDeptUsers: (id: number, params?: {
      page?: number;
      page_size?: number;
    }) => {
      return request({
        url: `/v1/system/dept/${id}/users`,
        method: 'GET',
        params,
      });
    },
    
    // 兼容旧API：保存或更新
    saveOrUpdate: (data?: any) => {
      if (data?.id) {
        const { id, ...updateData } = data;
        return request({
          url: `/v1/system/dept/${id}`,
          method: 'PUT',
          data: updateData,
        });
      } else {
        return request({
          url: '/v1/system/dept',
          method: 'POST',
          data,
        });
      }
    },
    
    // 兼容旧API：删除
    deleted: (data?: any) => {
      if (data?.id) {
        return request({
          url: `/v1/system/dept/${data.id}`,
          method: 'DELETE',
        });
      }
      throw new Error('缺少部门ID');
    },
  };
}
