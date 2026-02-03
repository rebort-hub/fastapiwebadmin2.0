<template>
  <div class="monitor-server-container app-container">
    <el-row :gutter="20">
      <!-- 服务器基本信息 -->
      <el-col :span="24">
        <el-card class="mb20">
          <template #header>
            <div class="card-header">
              <span>服务器信息</span>
              <el-button type="primary" size="small" @click="refreshData">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <el-row :gutter="20" v-if="state.serverInfo">
            <el-col :span="6">
              <div class="info-item">
                <div class="info-label">主机名</div>
                <div class="info-value">{{ state.serverInfo.hostname }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="info-item">
                <div class="info-label">操作系统</div>
                <div class="info-value">{{ state.serverInfo.platform }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="info-item">
                <div class="info-label">系统架构</div>
                <div class="info-value">{{ state.serverInfo.architecture }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="info-item">
                <div class="info-label">启动时间</div>
                <div class="info-value">{{ state.serverInfo.boot_time }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- CPU信息 -->
      <el-col :span="12">
        <el-card class="mb20">
          <template #header>
            <span>CPU信息</span>
          </template>
          <div v-if="state.cpuInfo">
            <div class="progress-item">
              <div class="progress-label">CPU使用率</div>
              <el-progress 
                :percentage="state.cpuInfo.usage_percent" 
                :color="getCPUColor(state.cpuInfo.usage_percent)"
                :stroke-width="20"
              />
            </div>
            <el-row :gutter="10" class="mt15">
              <el-col :span="12">
                <div class="info-item">
                  <div class="info-label">物理核心</div>
                  <div class="info-value">{{ state.cpuInfo.physical_cores }}</div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="info-item">
                  <div class="info-label">逻辑核心</div>
                  <div class="info-value">{{ state.cpuInfo.logical_cores }}</div>
                </div>
              </el-col>
            </el-row>
            <el-row :gutter="10" class="mt10">
              <el-col :span="12">
                <div class="info-item">
                  <div class="info-label">当前频率</div>
                  <div class="info-value">{{ state.cpuInfo.current_frequency.toFixed(0) }} MHz</div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="info-item">
                  <div class="info-label">最大频率</div>
                  <div class="info-value">{{ state.cpuInfo.max_frequency.toFixed(0) }} MHz</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>

      <!-- 内存信息 -->
      <el-col :span="12">
        <el-card class="mb20">
          <template #header>
            <span>内存信息</span>
          </template>
          <div v-if="state.memoryInfo">
            <div class="progress-item">
              <div class="progress-label">内存使用率</div>
              <el-progress 
                :percentage="state.memoryInfo.usage_percent" 
                :color="getMemoryColor(state.memoryInfo.usage_percent)"
                :stroke-width="20"
              />
            </div>
            <el-row :gutter="10" class="mt15">
              <el-col :span="12">
                <div class="info-item">
                  <div class="info-label">总内存</div>
                  <div class="info-value">{{ formatBytes(state.memoryInfo.total) }}</div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="info-item">
                  <div class="info-label">已用内存</div>
                  <div class="info-value">{{ formatBytes(state.memoryInfo.used) }}</div>
                </div>
              </el-col>
            </el-row>
            <el-row :gutter="10" class="mt10">
              <el-col :span="12">
                <div class="info-item">
                  <div class="info-label">可用内存</div>
                  <div class="info-value">{{ formatBytes(state.memoryInfo.available) }}</div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="info-item">
                  <div class="info-label">交换分区</div>
                  <div class="info-value">{{ formatBytes(state.memoryInfo.swap_total) }}</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 磁盘信息 -->
      <el-col :span="12">
        <el-card class="mb20">
          <template #header>
            <span>磁盘信息</span>
          </template>
          <div v-if="state.diskInfo && state.diskInfo.length > 0">
            <div v-for="disk in state.diskInfo" :key="disk.device" class="disk-item">
              <div class="disk-header">
                <span class="disk-device">{{ disk.device }}</span>
                <span class="disk-mount">{{ disk.mountpoint }}</span>
              </div>
              <el-progress 
                :percentage="disk.usage_percent" 
                :color="getDiskColor(disk.usage_percent)"
                :stroke-width="15"
              />
              <div class="disk-info">
                <span>{{ formatBytes(disk.used) }} / {{ formatBytes(disk.total) }}</span>
                <span>剩余: {{ formatBytes(disk.free) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 网络信息 -->
      <el-col :span="12">
        <el-card class="mb20">
          <template #header>
            <span>网络信息</span>
          </template>
          <div v-if="state.networkInfo && state.networkInfo.length > 0">
            <div v-for="network in state.networkInfo" :key="network.interface" class="network-item">
              <div class="network-header">
                <span class="network-interface">{{ network.interface }}</span>
              </div>
              <el-row :gutter="10">
                <el-col :span="12">
                  <div class="info-item">
                    <div class="info-label">发送</div>
                    <div class="info-value">{{ formatBytes(network.bytes_sent) }}</div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="info-item">
                    <div class="info-label">接收</div>
                    <div class="info-value">{{ formatBytes(network.bytes_recv) }}</div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 进程信息 -->
    <el-row>
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>Top 进程</span>
          </template>
          <el-table :data="state.processInfo" style="width: 100%" stripe>
            <el-table-column prop="pid" label="PID" width="80" align="center" />
            <el-table-column prop="name" label="进程名" width="150" />
            <el-table-column prop="username" label="用户" width="100" />
            <el-table-column prop="status" label="状态" width="80" align="center" />
            <el-table-column prop="cpu_percent" label="CPU%" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="getCPUTagType(row.cpu_percent)" size="small">
                  {{ row.cpu_percent }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="memory_percent" label="内存%" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="getMemoryTagType(row.memory_percent)" size="small">
                  {{ row.memory_percent }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="memory_info" label="内存使用" width="100" align="center">
              <template #default="{ row }">
                {{ formatBytes(row.memory_info) }}
              </template>
            </el-table-column>
            <el-table-column prop="create_time" label="创建时间" width="150" />
            <el-table-column prop="cmdline" label="命令行" min-width="200" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup name="MonitorServer">
import { onMounted, reactive, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Refresh } from '@element-plus/icons-vue';
import { useServerMonitorApi, type ServerMonitorData } from '/@/api/v1/monitor/server';

interface StateRow {
  serverInfo: any;
  cpuInfo: any;
  memoryInfo: any;
  diskInfo: any[];
  networkInfo: any[];
  processInfo: any[];
  loading: boolean;
  timer: number | null;
}

const state = reactive<StateRow>({
  serverInfo: null,
  cpuInfo: null,
  memoryInfo: null,
  diskInfo: [],
  networkInfo: [],
  processInfo: [],
  loading: false,
  timer: null
});

const serverApi = useServerMonitorApi();

const loadData = async () => {
  if (state.loading) return;
  
  state.loading = true;
  try {
    const response = await serverApi.getServerInfo();
    if (response && response.data) {
      const data = response.data as ServerMonitorData;
      state.serverInfo = data.server_info;
      state.cpuInfo = data.cpu_info;
      state.memoryInfo = data.memory_info;
      state.diskInfo = data.disk_info;
      state.networkInfo = data.network_info;
      state.processInfo = data.top_processes;
    }
  } catch (error) {
    console.error('获取服务器监控数据失败:', error);
    ElMessage.error('获取服务器监控数据失败');
  } finally {
    state.loading = false;
  }
};

const refreshData = () => {
  loadData();
};

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const getCPUColor = (percentage: number): string => {
  if (percentage < 50) return '#67c23a';
  if (percentage < 80) return '#e6a23c';
  return '#f56c6c';
};

const getMemoryColor = (percentage: number): string => {
  if (percentage < 60) return '#67c23a';
  if (percentage < 85) return '#e6a23c';
  return '#f56c6c';
};

const getDiskColor = (percentage: number): string => {
  if (percentage < 70) return '#67c23a';
  if (percentage < 90) return '#e6a23c';
  return '#f56c6c';
};

const getCPUTagType = (percentage: number): string => {
  if (percentage < 50) return 'success';
  if (percentage < 80) return 'warning';
  return 'danger';
};

const getMemoryTagType = (percentage: number): string => {
  if (percentage < 60) return 'success';
  if (percentage < 85) return 'warning';
  return 'danger';
};

onMounted(() => {
  loadData();
  // 每30秒自动刷新
  state.timer = window.setInterval(() => {
    loadData();
  }, 30000);
});

onUnmounted(() => {
  if (state.timer) {
    clearInterval(state.timer);
  }
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-item {
  text-align: center;
  padding: 10px;
}

.info-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.info-value {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.progress-item {
  margin-bottom: 15px;
}

.progress-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.disk-item {
  margin-bottom: 20px;
}

.disk-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.disk-device {
  font-weight: bold;
  color: #303133;
}

.disk-mount {
  color: #909399;
  font-size: 12px;
}

.disk-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.network-item {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.network-item:last-child {
  border-bottom: none;
}

.network-header {
  margin-bottom: 10px;
}

.network-interface {
  font-weight: bold;
  color: #303133;
}
</style>