/**
 * 在线用户监控API
 */

import request from '/@/utils/request';

export interface OnlineUserInfo {
  user_id: number;
  username: string;
  nickname: string;
  avatar?: string;
  login_time: string;
  last_activity: string;
  ip_address: string;
  location: string;
  browser: string;
  os: string;
  user_agent: string;
  session_id: string;
  is_active: boolean;
  duration: string;
}

export interface OnlineUserStats {
  total_online: number;
  active_users: number;
  new_today: number;
  peak_today: number;
  avg_duration: string;
}

export interface OnlineUserListResponse {
  items: OnlineUserInfo[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

/**
 * 在线用户监控API类
 */
export function useOnlineUserApi() {
  return {
    /**
     * 获取在线用户列表
     */
    getOnlineUsers: (params: {
      page?: number;
      page_size?: number;
    }): Promise<IApiResponseData<OnlineUserListResponse>> => {
      return request({
        url: '/v1/monitor/online/users',
        method: 'get',
        params,
      });
    },

    /**
     * 获取在线用户统计
     */
    getOnlineStats: (): Promise<IApiResponseData<OnlineUserStats>> => {
      return request({
        url: '/v1/monitor/online/stats',
        method: 'get',
      });
    },

    /**
     * 强制用户下线
     */
    forceOffline: (userId: number, sessionId?: string): Promise<IApiResponseData<any>> => {
      const params = sessionId ? { session_id: sessionId } : {};
      return request({
        url: `/v1/monitor/online/force-offline/${userId}`,
        method: 'post',
        params,
      });
    },

    /**
     * 清理过期用户
     */
    cleanupExpiredUsers: (): Promise<IApiResponseData<any>> => {
      return request({
        url: '/v1/monitor/online/cleanup',
        method: 'post',
      });
    },
  };
}