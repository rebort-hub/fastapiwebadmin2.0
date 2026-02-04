<template>
  <div class="app-container">
    <!-- CPU 和 内存使用情况 -->
    <el-row :gutter="16">
      <el-col :span="12" class="mb-4">
        <el-card :loading="state.loading" shadow="hover">
          <template #header>
            <div class="flex items-center gap-2">
              <el-icon><Cpu /></el-icon>
              <span>CPU使用情况</span>
              <el-tooltip content="展示CPU核心数及使用率">
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <el-row :gutter="16" v-if="state.cpuInfo">
            <!-- CPU核心数卡片 -->
            <el-col :span="12">
              <el-card shadow="hover">
                <span class="card-title">核心数</span>
                <el-tooltip :content="`物理核心: ${state.cpuInfo.physical_cores}, 逻辑核心: ${state.cpuInfo.logical_cores}`">
                  <div class="text-center mb-4">
                    <el-progress
                      type="circle"
                      :percentage="100"
                      :format="() => `${state.cpuInfo.logical_cores}`"
                    />
                  </div>
                </el-tooltip>
                <el-descriptions :column="1" border size="small">
                  <el-descriptions-item label="物理核心">
                    {{ state.cpuInfo.physical_cores }}
                  </el-descriptions-item>
                  <el-descriptions-item label="逻辑核心">
                    {{ state.cpuInfo.logical_cores }}
                  </el-descriptions-item>
                  <el-descriptions-item label="当前频率">
                    {{ state.cpuInfo.current_frequency.toFixed(0) }} MHz
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
            <!-- CPU使用率卡片 -->
            <el-col :span="12">
              <el-card shadow="hover" class="h-full">
                <span class="card-title">使用率</span>
                <el-tooltip :content="state.cpuInfo.usage_percent.toFixed(1) + '%'">
                  <div class="text-center mb-4">
                    <el-progress
                      type="circle"
                      :percentage="state.cpuInfo.usage_percent"
                      :status="
                        state.cpuInfo.usage_percent > 80
                          ? 'exception'
                          : state.cpuInfo.usage_percent > 60
                            ? 'warning'
                            : 'success'
                      "
                    />
                  </div>
                </el-tooltip>
                <el-descriptions :column="1" border size="small">
                  <el-descriptions-item label="CPU使用率">
                    {{ state.cpuInfo.usage_percent.toFixed(1) }}%
                  </el-descriptions-item>
                  <el-descriptions-item label="最大频率">
                    {{ state.cpuInfo.max_frequency.toFixed(0) }} MHz
                  </el-descriptions-item>
                  <el-descriptions-item label="最小频率">
                    {{ state.cpuInfo.min_frequency.toFixed(0) }} MHz
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <el-col :span="12" class="mb-4">
        <el-card :loading="state.loading" shadow="hover">
          <template #header>
            <div class="flex items-center gap-2">
              <el-icon><Memo /></el-icon>
              <span>内存使用情况</span>
              <el-tooltip content="展示系统内存和交换分区使用情况">
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <el-row :gutter="16" v-if="state.memoryInfo">
            <!-- 系统内存卡片 -->
            <el-col :span="12">
              <el-card shadow="hover" class="h-full">
                <span class="card-title">系统内存</span>
                <el-tooltip :content="state.memoryInfo.usage_percent.toFixed(1) + '%'">
                  <div class="text-center mb-4">
                    <el-progress
                      type="circle"
                      :percentage="state.memoryInfo.usage_percent"
                      :status="
                        state.memoryInfo.usage_percent > 80
                          ? 'exception'
                          : state.memoryInfo.usage_percent > 60
                            ? 'warning'
                            : 'success'
                      "
                    />
                  </div>
                </el-tooltip>
                <el-descriptions :column="1" border size="small">
                  <el-descriptions-item label="总内存">
                    {{ formatBytes(state.memoryInfo.total) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="已用内存">
                    {{ formatBytes(state.memoryInfo.used) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="可用内存">
                    {{ formatBytes(state.memoryInfo.available) }}
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
            <!-- 交换分区卡片 -->
            <el-col :span="12">
              <el-card shadow="hover" class="h-full">
                <span class="card-title">交换分区</span>
                <el-tooltip :content="state.memoryInfo.swap_percent.toFixed(1) + '%'">
                  <div class="text-center mb-4">
                    <el-progress
                      type="circle"
                      :percentage="state.memoryInfo.swap_percent"
                      :status="
                        state.memoryInfo.swap_percent > 80
                          ? 'exception'
                          : state.memoryInfo.swap_percent > 60
                            ? 'warning'
                            : 'success'
                      "
                    />
                  </div>
                </el-tooltip>
                <el-descriptions :column="1" border size="small">
                  <el-descriptions-item label="总大小">
                    {{ formatBytes(state.memoryInfo.swap_total) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="已用">
                    {{ formatBytes(state.memoryInfo.swap_used) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="空闲">
                    {{ formatBytes(state.memoryInfo.swap_free) }}
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 服务器基本信息 -->
    <el-row>
      <el-col :span="24" class="mb-4">
        <el-card :loading="state.loading" shadow="hover">
          <template #header>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <el-icon><Monitor /></el-icon>
                <span class="font-medium">服务器基本信息</span>
                <el-tooltip content="展示服务器基本配置信息">
                  <el-icon><QuestionFilled /></el-icon>
                </el-tooltip>
              </div>
              <el-button type="primary" size="small" @click="refreshData">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <el-descriptions :column="3" border v-if="state.serverInfo">
            <el-descriptions-item label="主机名">
              {{ state.serverInfo.hostname }}
            </el-descriptions-item>
            <el-descriptions-item label="操作系统">
              {{ state.serverInfo.platform }}
            </el-descriptions-item>
            <el-descriptions-item label="系统架构">
              {{ state.serverInfo.architecture }}
            </el-descriptions-item>
            <el-descriptions-item label="处理器">
              {{ state.serverInfo.processor }}
            </el-descriptions-item>
            <el-descriptions-item label="启动时间">
              {{ state.serverInfo.boot_time }}
            </el-descriptions-item>
            <el-descriptions-item label="运行时长">
              {{ state.serverInfo.uptime }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <!-- 磁盘使用情况 -->
    <el-row>
      <el-col :span="24" class="mb-4">
        <el-card :loading="state.loading" shadow="hover">
          <template #header>
            <div class="flex items-center gap-2">
              <el-icon><Files /></el-icon>
              <span class="font-medium">磁盘使用情况</span>
              <el-tooltip content="展示磁盘空间使用详情">
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <el-table :data="state.diskInfo" border>
            <template #empty>
              <el-empty :image-size="80" description="暂无数据" />
            </template>
            <el-table-column label="设备" prop="device" :show-overflow-tooltip="true" min-width="120" />
            <el-table-column label="挂载点" prop="mountpoint" :show-overflow-tooltip="true" min-width="120" />
            <el-table-column label="文件系统" prop="fstype" align="center" min-width="100" />
            <el-table-column prop="usage_percent" label="使用率" align="center" min-width="180">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.usage_percent"
                  :status="row.usage_percent > 80 ? 'exception' : row.usage_percent > 60 ? 'warning' : 'success'"
                  :text-inside="true"
                  :stroke-width="16"
                />
              </template>
            </el-table-column>
            <el-table-column label="总大小" align="center" min-width="100">
              <template #default="{ row }">
                {{ formatBytes(row.total) }}
              </template>
            </el-table-column>
            <el-table-column label="已用" align="center" min-width="100">
              <template #default="{ row }">
                {{ formatBytes(row.used) }}
              </template>
            </el-table-column>
            <el-table-column label="可用" align="center" min-width="100">
              <template #default="{ row }">
                {{ formatBytes(row.free) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 网络信息 -->
    <el-row>
      <el-col :span="24" class="mb-4">
        <el-card :loading="state.loading" shadow="hover">
          <template #header>
            <div class="flex items-center gap-2">
              <el-icon><Connection /></el-icon>
              <span class="font-medium">网络使用情况</span>
              <el-tooltip content="展示网络接口流量统计">
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <el-table :data="state.networkInfo" border>
            <template #empty>
              <el-empty :image-size="80" description="暂无数据" />
            </template>
            <el-table-column label="网络接口" prop="interface" min-width="120" />
            <el-table-column label="发送字节" align="center" min-width="120">
              <template #default="{ row }">
                {{ formatBytes(row.bytes_sent) }}
              </template>
            </el-table-column>
            <el-table-column label="接收字节" align="center" min-width="120">
              <template #default="{ row }">
                {{ formatBytes(row.bytes_recv) }}
              </template>
            </el-table-column>
            <el-table-column label="发送包" prop="packets_sent" align="center" min-width="100" />
            <el-table-column label="接收包" prop="packets_recv" align="center" min-width="100" />
            <el-table-column label="发送错误" prop="errout" align="center" min-width="90" />
            <el-table-column label="接收错误" prop="errin" align="center" min-width="90" />
            <el-table-column label="发送丢包" prop="dropout" align="center" min-width="90" />
            <el-table-column label="接收丢包" prop="dropin" align="center" min-width="90" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Top 进程 -->
    <el-row>
      <el-col :span="24">
        <el-card :loading="state.loading" shadow="hover">
          <template #header>
            <div class="flex items-center gap-2">
              <el-icon><List /></el-icon>
              <span class="font-medium">Top 进程</span>
              <el-tooltip content="展示CPU占用最高的进程">
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
          <el-table :data="state.processInfo" border stripe>
            <template #empty>
              <el-empty :image-size="80" description="暂无数据" />
            </template>
            <el-table-column prop="pid" label="PID" min-width="80" align="center" />
            <el-table-column prop="name" label="进程名" min-width="150" :show-overflow-tooltip="true" />
            <el-table-column prop="username" label="用户" min-width="100" />
            <el-table-column prop="status" label="状态" min-width="80" align="center" />
            <el-table-column prop="cpu_percent" label="CPU%" min-width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="getCPUTagType(row.cpu_percent)" size="small">
                  {{ row.cpu_percent }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="memory_percent" label="内存%" min-width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="getMemoryTagType(row.memory_percent)" size="small">
                  {{ row.memory_percent }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="内存使用" min-width="110" align="center">
              <template #default="{ row }">
                {{ formatBytes(row.memory_info) }}
              </template>
            </el-table-column>
            <el-table-column prop="create_time" label="创建时间" min-width="150" />
            <el-table-column prop="cmdline" label="命令行" min-width="200" :show-overflow-tooltip="true" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup name="MonitorServer">
import { onMounted, reactive, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import { 
  Refresh, Cpu, Memo, Monitor, QuestionFilled, 
  Files, Connection, List 
} from '@element-plus/icons-vue';
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

<style lang="scss" scoped>
.mb-4 {
  margin-bottom: 16px;
}

.flex {
  display: flex;
}

.items-center {
  align-items: center;
}

.justify-between {
  justify-content: space-between;
}

.gap-2 {
  gap: 8px;
}

.text-center {
  text-align: center;
}

.font-medium {
  font-weight: 500;
}

.h-full {
  height: 100%;
}

.card-title {
  display: block;
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
  font-weight: 500;
}

:deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-descriptions__label) {
  font-weight: 500;
}

:deep(.el-progress-circle) {
  width: 120px !important;
  height: 120px !important;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  font-weight: 600;
}
</style>