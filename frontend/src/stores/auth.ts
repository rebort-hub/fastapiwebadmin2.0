import { defineStore } from "pinia";
import { useUserStore } from "/@/stores/user";
import { useUserApi } from "/@/api/v1/system/user";
import { Session } from "/@/utils/storage";
import { initBackEndControlRoutes } from "/@/router/backEnd";
import { resetAllStores } from "/@/stores/setup";

export const useAuthStore = defineStore("auth", () => {
	const userStore = useUserStore();


	async function Login(params: any) {
		const { data } = await useUserApi().signIn(params)
		// 新API返回access_token，兼容旧的token字段
		const token = data?.access_token || data?.token
		Session.set('token', token);
		// 如果有refresh_token，也保存
		if (data?.refresh_token) {
			Session.set('refresh_token', data.refresh_token);
		}
		await userStore.setUserInfos();
		await initBackEndControlRoutes();
	}

	async function Logout() {
		await useUserApi().logout();
		Session.clear();
		resetAllStores()
	}

	return {
		Login,
		Logout
	}

})