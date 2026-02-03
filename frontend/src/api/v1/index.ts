/**
 * API v1 统一导出
 * 新架构API模块
 */

// 系统管理模块
export { useAuthApi } from './system/auth';
export { useUserApi } from './system/user';
export { useRoleApi } from './system/role';
export { useMenuApi } from './system/menu';
export { useDeptApi } from './system/dept';
export { useDictTypeApi, useDictDataApi, useDictApi } from './system/dict';
export { usePermissionApi } from './system/permission';
export { useLogApi } from './system/log';

// 通用模块
export { useFileApi } from './common/file';
export { useHealthApi } from './common/health';
