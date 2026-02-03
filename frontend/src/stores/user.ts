import {defineStore} from 'pinia';
import {Session} from '/@/utils/storage';
import {useUserApi} from "/@/api/v1/system/user";

/**
 * 用户信息
 * @methods setUserInfos 设置用户信息
 */
export const useUserStore = defineStore('userInfo', {
	state: (): UserInfosState => ({
		userInfos: {
			id: null,
			authBtnList: [],
			avatar: '',
			roles: [],
			time: 0,
			username: '',
			nickname: '',
			user_type: null,
			login_time: "",
			lastLoginTime: ""
		},
	}),

	actions: {
		async setUserInfos() {
			if (Session.get('userInfo')) {
				this.userInfos = Session.get('userInfo');
			} else {
				const apiUserInfo = await this.getApiUserInfo();
				
				// 处理头像URL：如果是相对路径，添加完整的基础URL
				let avatarUrl = apiUserInfo.avatar || '';
				if (avatarUrl && avatarUrl.startsWith('/static/')) {
					avatarUrl = `${import.meta.env.VITE_API_BASE_URL}${avatarUrl}`;
				}
				
				// 映射后端返回的数据到前端格式
				this.userInfos = {
					id: apiUserInfo.id?.toString() || null,
					authBtnList: apiUserInfo.permissions || [],  // 映射 permissions 到 authBtnList
					avatar: avatarUrl,
					roles: apiUserInfo.roles || [],
					time: Date.now(),
					username: apiUserInfo.username || '',
					nickname: apiUserInfo.nickname || '',
					user_type: apiUserInfo.user_type || null,
					login_time: apiUserInfo.last_login_time || '',
					lastLoginTime: apiUserInfo.last_login_time || ''
				};
				Session.set("userInfo", this.userInfos);
			}
		},
		async getApiUserInfo() {
			let {data} = await useUserApi().getUserInfoByToken()
			return data
		},
		async updateUserInfo(data: UserInfos) {
			this.userInfos = data
			Session.set("userInfo", data)
		}
	}
});