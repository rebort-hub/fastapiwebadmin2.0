import request from '/@/utils/request';

/**
 * 角色管理API - 新架构
 */
export function useRoleApi() {
  return {
    // 获取角色列表
    getList: (params?: {
      page?: number;
      pageSize?: number;
      page_size?: number;
      name?: string;
      role_code?: string;
      status?: number;
    }) => {
      // 转换参数：pageSize -> page_size
      const transformedParams = {
        ...params,
        page_size: params?.page_size || params?.pageSize || 10,
      };
      // 删除旧的pageSize参数
      if ('pageSize' in transformedParams) {
        delete (transformedParams as any).pageSize;
      }
      
      return request({
        url: '/v1/system/role',
        method: 'GET',
        params: transformedParams,
      });
    },
    
    // 获取角色详情
    getDetail: (id: number) => {
      return request({
        url: `/v1/system/role/${id}`,
        method: 'GET',
      });
    },
    
    // 创建角色
    create: (data: any) => {
      return request({
        url: '/v1/system/role',
        method: 'POST',
        data,
      });
    },
    
    // 更新角色
    update: (id: number, data: any) => {
      return request({
        url: `/v1/system/role/${id}`,
        method: 'PUT',
        data,
      });
    },
    
    // 删除角色
    delete: (id: number) => {
      return request({
        url: `/v1/system/role/${id}`,
        method: 'DELETE',
      });
    },
    
    // 批量删除角色
    batchDelete: (ids: number[]) => {
      return request({
        url: '/v1/system/role/batch',
        method: 'DELETE',
        data: { ids },
      });
    },
    
    // 分配菜单权限
    assignMenus: (id: number, data: { menu_ids: number[] }) => {
      return request({
        url: `/v1/system/role/${id}/menus`,
        method: 'POST',
        data,
      });
    },
    
    // 获取角色的菜单权限
    getRoleMenus: (id: number) => {
      return request({
        url: `/v1/system/role/${id}/menus`,
        method: 'GET',
      });
    },
    
    // 更新角色状态
    updateStatus: (id: number, status: number) => {
      return request({
        url: `/v1/system/role/${id}/status`,
        method: 'PUT',
        data: { status },
      });
    },
    
    // 设置数据权限
    setDataScope: (id: number, data: {
      data_scope: number;
      dept_ids?: number[];
    }) => {
      return request({
        url: `/v1/system/role/${id}/data-scope`,
        method: 'PUT',
        data,
      });
    },
    
    // 兼容旧API：保存或更新
    saveOrUpdate: (data?: any) => {
      if (data?.id) {
        const { id, ...updateData } = data;
        return request({
          url: `/v1/system/role/${id}`,
          method: 'PUT',
          data: updateData,
        });
      } else {
        return request({
          url: '/v1/system/role',
          method: 'POST',
          data,
        });
      }
    },
    
    // 兼容旧API：删除
    deleted: (data?: any) => {
      if (data?.id) {
        return request({
          url: `/v1/system/role/${data.id}`,
          method: 'DELETE',
        });
      }
      throw new Error('缺少角色ID');
    },
  };
}
