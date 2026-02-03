import request from '/@/utils/request';

/**
 * 用户管理API - 新架构
 */
export function useUserApi() {
  return {
    // 获取用户列表
    getList: (params?: {
      page?: number;
      pageSize?: number;
      page_size?: number;
      username?: string;
      nickname?: string;
      status?: number;
      dept_id?: number;
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
        url: '/v1/system/user',
        method: 'GET',
        params: transformedParams,
      });
    },
    
    // 获取用户详情
    getDetail: (id: number) => {
      return request({
        url: `/v1/system/user/${id}`,
        method: 'GET',
      });
    },
    
    // 创建用户
    create: (data: any) => {
      return request({
        url: '/v1/system/user',
        method: 'POST',
        data,
      });
    },
    
    // 更新用户
    update: (id: number, data: any) => {
      return request({
        url: `/v1/system/user/${id}`,
        method: 'PUT',
        data,
      });
    },
    
    // 删除用户
    delete: (id: number) => {
      return request({
        url: `/v1/system/user?ids=${id}`,
        method: 'DELETE',
      });
    },
    
    // 批量删除用户
    batchDelete: (ids: number[]) => {
      // 将数组转为多个ids参数：ids=1&ids=2&ids=3
      const idsParam = ids.map(id => `ids=${id}`).join('&');
      return request({
        url: `/v1/system/user?${idsParam}`,
        method: 'DELETE',
      });
    },
    
    // 重置密码（管理员）
    resetPassword: (id: number, data: { new_password: string }) => {
      return request({
        url: `/v1/system/user/${id}/reset-password`,
        method: 'PUT',  // 改为PUT方法
        data,
      });
    },
    
    // 修改密码（用户自己）
    changePassword: (data: {
      old_password: string;
      new_password: string;
      confirm_password: string;
    }) => {
      return request({
        url: '/v1/system/user/password',  // 使用新的路由，不需要user_id
        method: 'PUT',
        data,
      });
    },
    
    // 更新个人信息
    updateProfile: (data: {
      nickname?: string;
      remarks?: string;
      email?: string;
      tags?: string[];
    }) => {
      return request({
        url: '/v1/system/user/profile',
        method: 'PUT',
        data,
      });
    },
    
    // 更新头像
    updateAvatar: (data: { avatar: string }) => {
      return request({
        url: '/v1/system/user/avatar',
        method: 'PUT',
        data,
      });
    },
    
    // 分配角色
    assignRoles: (id: number, data: { role_ids: number[] }) => {
      return request({
        url: `/v1/system/user/${id}/roles`,
        method: 'POST',
        data,
      });
    },
    
    // 启用/禁用用户
    updateStatus: (id: number, status: number) => {
      return request({
        url: `/v1/system/user/${id}/status`,
        method: 'PUT',
        data: { status },
      });
    },
    
    // 兼容旧API：保存或更新
    saveOrUpdate: (data?: any) => {
      if (data?.id) {
        const { id, ...updateData } = data;
        return request({
          url: `/v1/system/user/${id}`,
          method: 'PUT',
          data: updateData,
        });
      } else {
        return request({
          url: '/v1/system/user',
          method: 'POST',
          data,
        });
      }
    },
    
    // 兼容旧API：删除
    deleted: (data?: any) => {
      if (data?.id) {
        // 使用多个ids参数的方式，FastAPI可以正确解析
        return request({
          url: `/v1/system/user?ids=${data.id}`,
          method: 'DELETE',
        });
      }
      throw new Error('缺少用户ID');
    },
    
    // 兼容旧API：管理员重置密码
    adminResetPassword: (data?: any) => {
      if (data?.id) {
        const { id } = data;
        // 默认重置密码为123456
        return request({
          url: `/v1/system/user/${id}/reset-password`,
          method: 'PUT',
          data: { new_password: '123456' },
        });
      }
      throw new Error('缺少用户ID');
    },
    
    // 兼容旧API：用户修改密码（使用changePassword代替）
    // resetPassword 已被标准方法占用，旧代码应使用 changePassword
    
    // 兼容旧API：更新头像
    updateUserAvatar: (data?: any) => {
      return request({
        url: '/v1/system/user/avatar',
        method: 'PUT',
        data,
      });
    },
    
    // 兼容旧API：获取用户信息
    getUserInfo: (data?: any) => {
      if (data?.id) {
        return request({
          url: `/v1/system/user/${data.id}`,
          method: 'GET',
        });
      }
      throw new Error('缺少用户ID');
    },
    
    // 兼容旧API：通过token获取菜单
    getMenuByToken: () => {
      return request({
        url: '/v1/system/auth/menus',
        method: 'GET',
      });
    },
    
    // 兼容旧API：通过token获取用户信息
    getUserInfoByToken: () => {
      return request({
        url: '/v1/system/auth/userinfo',
        method: 'GET',
      });
    },
    
    // 兼容旧API：登录（映射到auth API）
    signIn: (data: { username: string; password: string; captcha?: string }) => {
      return request({
        url: '/v1/system/auth/login',
        method: 'POST',
        data,
      });
    },
    
    // 兼容旧API：登出（映射到auth API）
    signOut: () => {
      return request({
        url: '/v1/system/auth/logout',
        method: 'POST',
      });
    },
    
    // 兼容旧API：登录（另一个名称）
    login: (data: { username: string; password: string; captcha?: string }) => {
      return request({
        url: '/v1/system/auth/login',
        method: 'POST',
        data,
      });
    },
    
    // 兼容旧API：登出（另一个名称）
    logout: () => {
      return request({
        url: '/v1/system/auth/logout',
        method: 'POST',
      });
    },
  };
}
