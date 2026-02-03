import request from '/@/utils/request';

/**
 * 文件管理API - 新架构
 */
export function useFileApi() {
  return {
    // 上传文件
    upload: (data: FormData) => {
      return request({
        url: '/v1/system/file/upload',
        method: 'POST',
        data,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    },
    
    // 批量上传文件
    batchUpload: (data: FormData) => {
      return request({
        url: '/v1/system/file/batch-upload',
        method: 'POST',
        data,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    },
    
    // 获取文件列表
    getList: (params?: {
      page?: number;
      page_size?: number;
      file_name?: string;
      original_name?: string;
      file_type?: string;
      file_ext?: string;
      upload_type?: string;
      is_public?: number;
      uploaded_by?: number;
      begin_time?: string;
      end_time?: string;
      tags?: string;
    }) => {
      return request({
        url: '/v1/system/file',
        method: 'GET',
        params,
      });
    },
    
    // 获取文件详情
    getDetail: (id: number) => {
      return request({
        url: `/v1/system/file/${id}`,
        method: 'GET',
      });
    },
    
    // 更新文件信息
    update: (id: number, data: {
      original_name?: string;
      description?: string;
      tags?: string;
      is_public?: number;
    }) => {
      return request({
        url: `/v1/system/file/${id}`,
        method: 'PUT',
        data,
      });
    },
    
    // 下载文件
    download: (id: number) => {
      return request({
        url: `/v1/system/file/${id}/download`,
        method: 'GET',
        responseType: 'blob',
      });
    },
    
    // 删除文件
    delete: (id: number) => {
      return request({
        url: `/v1/system/file/${id}`,
        method: 'DELETE',
      });
    },
    
    // 批量删除文件
    batchDelete: (ids: number[]) => {
      return request({
        url: '/v1/system/file/batch',
        method: 'DELETE',
        data: { ids },
      });
    },
    
    // 获取文件访问URL
    getUrl: (id: number) => {
      return request({
        url: `/v1/system/file/${id}/url`,
        method: 'GET',
      });
    },
    
    // 获取文件统计信息
    getStats: () => {
      return request({
        url: '/v1/system/file/stats/summary',
        method: 'GET',
      });
    },
    
    // 兼容旧API：上传文件
    uploadFile: (data: FormData) => {
      return request({
        url: '/v1/system/file/upload',
        method: 'POST',
        data,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    },
    
    // 兼容旧API：获取文件列表
    getFileList: (params?: any) => {
      // 转换参数格式
      const transformedParams = {
        page: params?.page || 1,
        page_size: params?.page_size || params?.pageSize || 10,
        file_name: params?.file_name || params?.fileName,
        original_name: params?.original_name || params?.originalName,
        file_type: params?.file_type || params?.fileType,
        begin_time: params?.begin_time || params?.beginTime,
        end_time: params?.end_time || params?.endTime,
      };
      
      return request({
        url: '/v1/system/file',
        method: 'GET',
        params: transformedParams,
      });
    },
    
    // 兼容旧API：删除文件
    deleteFile: (id: number) => {
      return request({
        url: `/v1/system/file/${id}`,
        method: 'DELETE',
      });
    },
    
    // 兼容旧API：下载文件
    downloadFile: (id: number) => {
      // 直接返回下载URL
      return `/api/v1/system/file/${id}/download`;
    },
  };
}
