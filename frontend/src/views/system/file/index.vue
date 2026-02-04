<template>
  <div class="file-management-container">
    <el-card shadow="hover">
      <!-- 操作栏 -->
      <div class="toolbar">
        <el-upload
          v-auth="'system:file:upload'"
          :action="uploadUrl"
          :headers="uploadHeaders"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :before-upload="beforeUpload"
          :show-file-list="false"
          name="file"
          multiple
        >
          <el-button type="primary" :icon="Upload">上传文件</el-button>
        </el-upload>
        
        <el-button :icon="Refresh" @click="getFileList">刷新</el-button>
        
        <div class="search-box">
          <el-input
            v-model="searchText"
            placeholder="搜索文件名"
            :prefix-icon="Search"
            clearable
            @clear="getFileList"
            @keyup.enter="getFileList"
            style="width: 300px"
          />
          <el-button type="primary" :icon="Search" @click="getFileList">搜索</el-button>
        </div>
      </div>

      <!-- 文件列表 -->
      <el-table
        v-loading="loading"
        :data="fileList"
        stripe
        style="width: 100%; margin-top: 20px"
      >
        <el-table-column type="index" label="序号" width="60" />
        
        <el-table-column prop="original_name" label="文件名" min-width="200">
          <template #default="{ row }">
            <el-tooltip :content="row.original_name" placement="top">
              <span class="file-name">{{ row.original_name }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        
        <el-table-column prop="file_ext" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.file_ext || '-' }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="formatted_size" label="大小" width="120">
          <template #default="{ row }">
            {{ row.formatted_size || formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="description" label="描述" min-width="150">
          <template #default="{ row }">
            {{ row.description || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="download_count" label="下载次数" width="100">
          <template #default="{ row }">
            {{ row.download_count || 0 }}
          </template>
        </el-table-column>
        
        <el-table-column prop="is_public" label="公开状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_public ? 'success' : 'warning'" size="small">
              {{ row.is_public ? '公开' : '私有' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="uploaded_by" label="上传者" width="120">
          <template #default="{ row }">
            {{ getUserName(row.uploaded_by) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <div class="operation-buttons">
              <el-button
                v-auth="'system:file:detail'"
                type="success"
                size="small"
                :icon="View"
                @click="viewFileDetail(row)"
              >
                详情
              </el-button>
              <el-button
                v-auth="'system:file:download'"
                type="primary"
                size="small"
                :icon="Download"
                @click="downloadFile(row)"
              >
                下载
              </el-button>
              <el-button
                v-auth="'system:file:edit'"
                type="info"
                size="small"
                @click="editFile(row)"
              >
                编辑
              </el-button>
              <el-button
                v-auth="'system:file:delete'"
                type="danger"
                size="small"
                :icon="Delete"
                @click="deleteFile(row)"
              >
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="getFileList"
          @current-change="getFileList"
        />
      </div>
    </el-card>

    <!-- 编辑文件对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑文件信息"
      width="500px"
      destroy-on-close
    >
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="文件名">
          <el-input v-model="editForm.original_name" placeholder="请输入文件名" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入文件描述"
          />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="editForm.tags" placeholder="请输入标签，多个标签用逗号分隔" />
        </el-form-item>
        <el-form-item label="公开状态">
          <el-radio-group v-model="editForm.is_public">
            <el-radio :label="1">公开</el-radio>
            <el-radio :label="0">私有</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveFileInfo">保存</el-button>
      </template>
    </el-dialog>

    <!-- 文件详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="文件详情"
      width="600px"
      destroy-on-close
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="文件名">
          {{ fileDetail.original_name }}
        </el-descriptions-item>
        <el-descriptions-item label="文件类型">
          <el-tag size="small">{{ fileDetail.file_ext || '-' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="文件大小">
          {{ fileDetail.formatted_size || formatFileSize(fileDetail.file_size) }}
        </el-descriptions-item>
        <el-descriptions-item label="下载次数">
          {{ fileDetail.download_count || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="公开状态">
          <el-tag :type="fileDetail.is_public ? 'success' : 'warning'" size="small">
            {{ fileDetail.is_public ? '公开' : '私有' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="上传者">
          {{ getUserName(fileDetail.uploaded_by) }}
        </el-descriptions-item>
        <el-descriptions-item label="上传时间">
          {{ formatDateTime(fileDetail.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ formatDateTime(fileDetail.updated_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">
          {{ fileDetail.description || '暂无描述' }}
        </el-descriptions-item>
        <el-descriptions-item label="标签" :span="2">
          <div v-if="fileDetail.tags">
            <el-tag
              v-for="tag in fileDetail.tags.split(',')"
              :key="tag"
              size="small"
              style="margin-right: 8px"
            >
              {{ tag.trim() }}
            </el-tag>
          </div>
          <span v-else>暂无标签</span>
        </el-descriptions-item>
        <el-descriptions-item label="文件路径" :span="2">
          <el-input
            :model-value="fileDetail.file_path"
            readonly
            size="small"
            style="font-family: monospace"
          />
        </el-descriptions-item>
        <el-descriptions-item label="访问URL" :span="2">
          <el-input
            :model-value="fileDetail.file_url"
            readonly
            size="small"
            style="font-family: monospace"
          >
            <template #append>
              <el-button @click="copyToClipboard(fileDetail.file_url)">复制</el-button>
            </template>
          </el-input>
        </el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" :icon="Download" @click="downloadFile(fileDetail)">下载文件</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts" name="fileManagement">
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Upload, Refresh, Search, Download, Delete, View } from '@element-plus/icons-vue';
import { useFileApi } from '/@/api/v1/common/file';
import { useUserApi } from '/@/api/v1/system/user';
import { formatDateTime } from '/@/utils/formatTime';
import { Session } from '/@/utils/storage';

// 数据
const loading = ref(false);
const fileList = ref<any[]>([]);
const searchText = ref('');
const page = ref(1);
const pageSize = ref(20);
const total = ref(0);

// 编辑对话框
const editDialogVisible = ref(false);
const editForm = ref({
  id: null,
  original_name: '',
  description: '',
  tags: '',
  is_public: 1,
});

// 详情对话框
const detailDialogVisible = ref(false);
const fileDetail = ref<any>({});

// 用户名映射（动态获取）
const userNameMap = ref<Record<number, string>>({});

// 获取用户信息
const loadUserInfo = async (userIds: number[]) => {
  try {
    // 过滤掉已经加载过的用户ID
    const newUserIds = userIds.filter(id => !userNameMap.value[id]);
    
    if (newUserIds.length === 0) return;
    
    // 批量获取用户信息
    for (const userId of newUserIds) {
      try {
        const res = await useUserApi().getDetail(userId);
        if (res.code === 200) {
          userNameMap.value[userId] = res.data.nickname || res.data.username || `用户${userId}`;
        } else {
          userNameMap.value[userId] = `用户${userId}`;
        }
      } catch (error) {
        userNameMap.value[userId] = `用户${userId}`;
      }
    }
  } catch (error) {
    console.error('获取用户信息失败:', error);
  }
};

// 上传配置
const uploadUrl = ref('http://127.0.0.1:8100/api/v1/system/file/upload');
const uploadHeaders = ref({
  Authorization: `Bearer ${Session.get('token') || 'test-token'}`,
});
const uploadData = ref({
  description: '前端上传文件',
  tags: '前端,上传',
  is_public: 1
});

// 获取用户名
const getUserName = (userId: number) => {
  return userNameMap.value[userId] || `用户${userId}`;
};

// 查看文件详情
const viewFileDetail = async (row: any) => {
  try {
    const res = await useFileApi().getDetail(row.id);
    if (res.code === 200) {
      fileDetail.value = res.data;
      
      // 确保上传者信息已加载
      await loadUserInfo([res.data.uploaded_by]);
      
      detailDialogVisible.value = true;
    } else {
      ElMessage.error(res.message || '获取文件详情失败');
    }
  } catch (error: any) {
    console.error('获取文件详情失败:', error);
    ElMessage.error(error.message || '获取文件详情失败');
  }
};

// 复制到剪贴板
const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success('已复制到剪贴板');
  } catch (error) {
    // 降级方案
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    ElMessage.success('已复制到剪贴板');
  }
};

// 获取文件列表
const getFileList = async () => {
  loading.value = true;
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      original_name: searchText.value || undefined,
    };
    
    const res = await useFileApi().getList(params);
    
    if (res.code === 200) {
      fileList.value = res.data.items || [];
      total.value = res.data.total || 0;
      
      // 获取所有上传者的用户信息
      const uploaderIds = [...new Set(fileList.value.map(item => item.uploaded_by))];
      await loadUserInfo(uploaderIds);
    } else {
      ElMessage.error(res.message || '获取文件列表失败');
    }
  } catch (error: any) {
    console.error('获取文件列表失败:', error);
    ElMessage.error(error.message || '获取文件列表失败');
  } finally {
    loading.value = false;
  }
};

// 上传前检查
const beforeUpload = (file: File) => {
  const maxSize = 50 * 1024 * 1024; // 50MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 50MB');
    return false;
  }
  
  // 检查文件类型
  const allowedTypes = [
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',  // 图片
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',  // 文档
    '.txt', '.md', '.csv',  // 文本
    '.zip', '.rar', '.7z', '.tar', '.gz',  // 压缩包
    '.mp4', '.avi', '.mov', '.wmv', '.flv',  // 视频
    '.mp3', '.wav', '.flac', '.aac'  // 音频
  ];
  
  const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
  if (!allowedTypes.includes(fileExt)) {
    ElMessage.error(`不支持的文件类型：${fileExt}`);
    return false;
  }
  
  return true;
};

// 上传成功
const handleUploadSuccess = (response: any) => {
  if (response.code === 200) {
    ElMessage.success('上传成功');
    getFileList();
  } else {
    ElMessage.error(response.message || '上传失败');
  }
};

// 上传失败
const handleUploadError = (error: any) => {
  console.error('上传失败:', error);
  ElMessage.error('上传失败');
};

// 下载文件
const downloadFile = async (row: any) => {
  try {
    // 使用API下载文件，这样会触发下载次数统计
    const response = await useFileApi().download(row.id);
    
    // 创建blob对象
    const blob = new Blob([response], { type: 'application/octet-stream' });
    const url = window.URL.createObjectURL(blob);
    
    // 创建下载链接
    const link = document.createElement('a');
    link.href = url;
    link.download = row.original_name;
    document.body.appendChild(link);
    link.click();
    
    // 清理
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    // 下载成功后刷新列表以更新下载次数
    await getFileList();
  } catch (error: any) {
    console.error('下载失败:', error);
    ElMessage.error(error.message || '下载失败');
  }
};

// 编辑文件
const editFile = (row: any) => {
  editForm.value = {
    id: row.id,
    original_name: row.original_name,
    description: row.description || '',
    tags: row.tags || '',
    is_public: row.is_public,
  };
  editDialogVisible.value = true;
};

// 保存文件信息
const saveFileInfo = async () => {
  try {
    const { id, ...updateData } = editForm.value;
    await useFileApi().update(id, updateData);
    ElMessage.success('更新成功');
    editDialogVisible.value = false;
    getFileList();
  } catch (error: any) {
    console.error('更新失败:', error);
    ElMessage.error(error.message || '更新失败');
  }
};

// 删除文件
const deleteFile = (row: any) => {
  ElMessageBox.confirm(`确定要删除文件 "${row.original_name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await useFileApi().delete(row.id);
      ElMessage.success('删除成功');
      getFileList();
    } catch (error: any) {
      console.error('删除失败:', error);
      ElMessage.error(error.message || '删除失败');
    }
  }).catch(() => {});
};

// 格式化文件大小
const formatFileSize = (size: string | number) => {
  if (!size) return '-';
  
  const sizeInBytes = typeof size === 'string' ? parseInt(size) : size;
  if (isNaN(sizeInBytes)) return '-';
  
  if (sizeInBytes === 0) return '0 B';
  
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(sizeInBytes) / Math.log(1024));
  
  if (i === 0) {
    return `${sizeInBytes} ${sizes[i]}`;
  } else {
    return `${(sizeInBytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
  }
};

// 初始化
onMounted(() => {
  getFileList();
});
</script>

<style scoped lang="scss">
.file-management-container {
  padding: 20px;

  .toolbar {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;

    .search-box {
      display: flex;
      gap: 10px;
      margin-left: auto;
    }
  }

  .file-name {
    display: inline-block;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .operation-buttons {
    display: flex;
    gap: 8px;
    align-items: center;
    white-space: nowrap;
    
    .el-button {
      margin: 0;
    }
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
