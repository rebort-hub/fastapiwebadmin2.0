import request from '/@/utils/request';

/**
 * 字典管理API - 新架构
 */

// ==================== 字典类型 ====================

export function useDictTypeApi() {
  return {
    // 获取字典类型列表（分页）
    getList: (params?: {
      page?: number;
      page_size?: number;
      dict_name?: string;
      dict_type?: string;
      status?: number;
      begin_time?: string;
      end_time?: string;
    }) => {
      return request({
        url: '/v1/system/dict/type/list/all',
        method: 'GET',
        params,
      });
    },
    
    // 获取字典类型详情
    getDetail: (id: number) => {
      return request({
        url: `/v1/system/dict/type/${id}`,
        method: 'GET',
      });
    },
    
    // 创建字典类型
    create: (data: any) => {
      return request({
        url: '/v1/system/dict/type',
        method: 'POST',
        data,
      });
    },
    
    // 更新字典类型
    update: (id: number, data: any) => {
      return request({
        url: `/v1/system/dict/type/${id}`,
        method: 'PUT',
        data,
      });
    },
    
    // 删除字典类型（单个）
    delete: (id: number) => {
      return request({
        url: `/v1/system/dict/type/${id}`,
        method: 'DELETE',
      });
    },
    
    // 删除字典类型（批量）
    deleteBatch: (ids: number[]) => {
      return request({
        url: '/v1/system/dict/type',
        method: 'DELETE',
        params: { ids },
      });
    },
    
    // 保存或更新（兼容旧API）
    saveOrUpdate: (data: any) => {
      if (data.id) {
        const { id, ...updateData } = data;
        return request({
          url: `/v1/system/dict/type/${id}`,
          method: 'PUT',
          data: updateData,
        });
      } else {
        return request({
          url: '/v1/system/dict/type',
          method: 'POST',
          data,
        });
      }
    },
  };
}

// ==================== 字典数据 ====================

export function useDictDataApi() {
  return {
    // 获取字典数据列表（分页）
    getList: (params?: {
      page?: number;
      page_size?: number;
      dict_label?: string;
      dict_type?: string;
      status?: number;
    }) => {
      return request({
        url: '/v1/system/dict/data/list/all',
        method: 'GET',
        params,
      });
    },
    
    // 根据字典类型获取数据
    getByType: (dictType: string) => {
      return request({
        url: `/v1/system/dict/data/type/${dictType}`,
        method: 'GET',
      });
    },
    
    // 获取字典数据详情
    getDetail: (id: number) => {
      return request({
        url: `/v1/system/dict/data/${id}`,
        method: 'GET',
      });
    },
    
    // 创建字典数据
    create: (data: any) => {
      return request({
        url: '/v1/system/dict/data',
        method: 'POST',
        data,
      });
    },
    
    // 更新字典数据
    update: (id: number, data: any) => {
      return request({
        url: `/v1/system/dict/data/${id}`,
        method: 'PUT',
        data,
      });
    },
    
    // 删除字典数据（单个）
    delete: (id: number) => {
      return request({
        url: `/v1/system/dict/data/${id}`,
        method: 'DELETE',
      });
    },
    
    // 删除字典数据（批量）
    deleteBatch: (ids: number[]) => {
      return request({
        url: '/v1/system/dict/data',
        method: 'DELETE',
        params: { ids },
      });
    },
    
    // 保存或更新（兼容旧API）
    saveOrUpdate: (data: any) => {
      if (data.id) {
        const { id, ...updateData } = data;
        return request({
          url: `/v1/system/dict/data/${id}`,
          method: 'PUT',
          data: updateData,
        });
      } else {
        return request({
          url: '/v1/system/dict/data',
          method: 'POST',
          data,
        });
      }
    },
  };
}


// ==================== 兼容旧API ====================
// 为了兼容旧的lookup页面，提供useDictApi别名
export function useDictApi() {
  // 返回一个空对象，避免报错
  // 如果需要使用lookup功能，请使用useDictTypeApi或useDictDataApi
  return {
    getList: () => useDictTypeApi().getList(),
    getLookupList: (params: any) => {
      console.warn('getLookupList is deprecated, please use useDictTypeApi().getList()');
      return useDictTypeApi().getList(params);
    },
    saveOrUpdateLookup: (data: any) => {
      console.warn('saveOrUpdateLookup is deprecated, please use useDictTypeApi().saveOrUpdate()');
      return useDictTypeApi().saveOrUpdate(data);
    },
    delLookup: (data: any) => {
      console.warn('delLookup is deprecated, please use useDictTypeApi().delete()');
      return useDictTypeApi().delete(data.id);
    },
    getLookupValue: (params: any) => {
      console.warn('getLookupValue is deprecated, please use useDictDataApi().getList()');
      return useDictDataApi().getList(params);
    },
    saveOrUpdateLookupValue: (data: any) => {
      console.warn('saveOrUpdateLookupValue is deprecated, please use useDictDataApi().saveOrUpdate()');
      return useDictDataApi().saveOrUpdate(data);
    },
    delLookupValue: (data: any) => {
      console.warn('delLookupValue is deprecated, please use useDictDataApi().delete()');
      return useDictDataApi().delete(data.id);
    },
  };
}
