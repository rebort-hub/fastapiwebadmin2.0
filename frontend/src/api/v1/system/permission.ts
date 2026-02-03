import request from '/@/utils/request';

/**
 * 权限管理API
 */
export function usePermissionApi() {
  return {
    // 获取权限列表
    getList: (params?: {
      page?: number;
      page_size?: number;
      permission_code?: string;
      permission_name?: string;
      permission_type?: number;
      status?: number;
    }) => {
      return request({
        url: '/v1/system/permission/list/all',
        method: 'GET',
        params,
      });
    },
    
    // 获取权限详情
    getDetail: (id: number) => {
      return request({
        url: `/v1/system/permission/${id}`,
        method: 'GET',
      });
    },
    
    // 创建权限
    create: (data: {
      permission_code: string;
      permission_name: string;
      permission_type: number;
      resource_type?: string;
      resource_id?: number;
      description?: string;
      status?: number;
      sort?: number;
    }) => {
      return request({
        url: '/v1/system/permission',
        method: 'POST',
        data,
      });
    },
    
    // 更新权限
    update: (id: number, data: any) => {
      return request({
        url: `/v1/system/permission/${id}`,
        method: 'PUT',
        data,
      });
    },
    
    // 删除权限
    delete: (id: number) => {
      return request({
        url: `/v1/system/permission?ids=${id}`,
        method: 'DELETE',
      });
    },
    
    // 批量删除权限
    batchDelete: (ids: number[]) => {
      const idsParam = ids.map(id => `ids=${id}`).join('&');
      return request({
        url: `/v1/system/permission?${idsParam}`,
        method: 'DELETE',
      });
    },
    
    // 获取所有启用的权限
    getAllEnabled: () => {
      return request({
        url: '/v1/system/permission/all/enabled',
        method: 'GET',
      });
    },
    
    // 获取权限类型选项
    getPermissionTypes: () => {
      return Promise.resolve({
        data: [
          { value: 1, label: '菜单权限' },
          { value: 2, label: '按钮权限' },
          { value: 3, label: '数据权限' },
          { value: 4, label: 'API权限' }
        ]
      });
    },
    
    // 获取数据权限范围选项
    getDataScopes: () => {
      return Promise.resolve({
        data: [
          { value: 1, label: '仅本人数据' },
          { value: 2, label: '本部门数据' },
          { value: 3, label: '本部门及以下数据' },
          { value: 4, label: '全部数据' },
          { value: 5, label: '自定义数据' }
        ]
      });
    },
    
    // 批量创建API权限
    batchCreateApiPermissions: (data: {
      module: string;
      permissions: Array<{
        action: string;
        name: string;
        description?: string;
      }>;
    }) => {
      return request({
        url: '/v1/system/permission/batch-create-api',
        method: 'POST',
        data,
      });
    },
    
    // 同步菜单权限
    syncMenuPermissions: () => {
      return request({
        url: '/v1/system/permission/sync-menu',
        method: 'POST',
      });
    },
    
    // 兼容旧API：保存或更新
    saveOrUpdate: (data?: any) => {
      if (data?.id) {
        const { id, ...updateData } = data;
        return request({
          url: `/v1/system/permission/${id}`,
          method: 'PUT',
          data: updateData,
        });
      } else {
        return request({
          url: '/v1/system/permission',
          method: 'POST',
          data,
        });
      }
    },
    
    // 兼容旧API：删除
    deleted: (data?: any) => {
      if (data?.id) {
        return request({
          url: `/v1/system/permission?ids=${data.id}`,
          method: 'DELETE',
        });
      }
      throw new Error('缺少权限ID');
    },
  };
}