import request from '/@/utils/request';

/**
 * 菜单管理API - 新架构
 */
export function useMenuApi() {
  return {
    // 获取菜单列表
    getList: (params?: {
      title?: string;
      status?: number;
      menu_type?: number;
    }) => {
      return request({
        url: '/v1/system/menu',
        method: 'GET',
        params,
      });
    },
    
    // 获取菜单树
    getTree: (params?: {
      status?: number;
      menu_type?: number;
    }) => {
      return request({
        url: '/v1/system/menu/tree',
        method: 'GET',
        params,
      });
    },
    
    // 获取菜单详情
    getDetail: (id: number) => {
      return request({
        url: `/v1/system/menu/${id}`,
        method: 'GET',
      });
    },
    
    // 创建菜单
    create: (data: any) => {
      return request({
        url: '/v1/system/menu',
        method: 'POST',
        data,
      });
    },
    
    // 更新菜单
    update: (id: number, data: any) => {
      return request({
        url: `/v1/system/menu/${id}`,
        method: 'PUT',
        data,
      });
    },
    
    // 删除菜单
    delete: (id: number) => {
      return request({
        url: `/v1/system/menu/${id}`,
        method: 'DELETE',
      });
    },
    
    // 更新菜单状态
    updateStatus: (id: number, status: number) => {
      return request({
        url: `/v1/system/menu/${id}/status`,
        method: 'PUT',
        data: { status },
      });
    },
    
    // 更新菜单排序
    updateSort: (id: number, sort: number) => {
      return request({
        url: `/v1/system/menu/${id}/sort`,
        method: 'PUT',
        data: { sort },
      });
    },
    
    // 获取按钮权限列表
    getButtons: (params?: { parent_id?: number }) => {
      return request({
        url: '/v1/system/menu/buttons',
        method: 'GET',
        params,
      });
    },
    
    // 兼容旧API：获取所有菜单（嵌套格式）
    getAllMenus: () => {
      return request({
        url: '/v1/system/menu/tree',
        method: 'GET',
      });
    },
    
    // 兼容旧API：获取所有菜单（平铺格式）
    allMenu: (data?: any) => {
      return request({
        url: '/v1/system/menu',
        method: 'GET',
        params: data,
      });
    },
    
    // 兼容旧API：保存或更新
    saveOrUpdate: (data?: any) => {
      if (data?.id) {
        const { id, ...updateData } = data;
        return request({
          url: `/v1/system/menu/${id}`,
          method: 'PUT',
          data: updateData,
        });
      } else {
        return request({
          url: '/v1/system/menu',
          method: 'POST',
          data,
        });
      }
    },
    
    // 兼容旧API：删除
    deleted: (data?: any) => {
      if (data?.id) {
        return request({
          url: `/v1/system/menu/${data.id}`,
          method: 'DELETE',
        });
      }
      throw new Error('缺少菜单ID');
    },
  };
}
