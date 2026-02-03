import request from '/@/utils/request';

/**
 * 认证API - 新架构
 */
export function useAuthApi() {
  return {
    // 登录
    login: (data: { username: string; password: string; captcha?: string }) => {
      return request({
        url: '/v1/system/auth/login',
        method: 'POST',
        data,
      });
    },
    
    // 登出
    logout: () => {
      return request({
        url: '/v1/system/auth/logout',
        method: 'POST',
      });
    },
    
    // 刷新Token
    refreshToken: (data: { refresh_token: string }) => {
      return request({
        url: '/v1/system/auth/refresh',
        method: 'POST',
        data,
      });
    },
    
    // 获取当前用户信息
    getUserInfo: () => {
      return request({
        url: '/v1/system/auth/userinfo',
        method: 'GET',
      });
    },
    
    // 获取当前用户菜单
    getUserMenus: () => {
      return request({
        url: '/v1/system/auth/menus',
        method: 'GET',
      });
    },
    
    // 获取当前用户权限
    getUserPermissions: () => {
      return request({
        url: '/v1/system/auth/permissions',
        method: 'GET',
      });
    },
  };
}
