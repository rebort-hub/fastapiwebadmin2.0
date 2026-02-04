<template>
  <div class="monitor-online-container app-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="mb20">
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-item">
            <div class="stats-icon online">
              <el-icon><User /></el-icon>
            </div>
            <div class="stats-content">
              <div class="stats-value">{{ state.stats.total_online }}</div>
              <div class="stats-label">在线用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-item">
            <div class="stats-icon active">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="stats-content">
              <div class="stats-value">{{ state.stats.active_users }}</div>
              <div class="stats-label">活跃用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-item">
            <div class="stats-icon new">
              <el-icon><Plus /></el-icon>
            </div>
            <div class="stats-content">
              <div class="stats-value">{{ state.stats.new_today }}</div>
              <div class="stats-label">今日新增</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-item">
            <div class="stats-icon duration">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="stats-content">
              <div class="stats-value">{{ state.stats.avg_duration }}</div>
              <div class="stats-label">平均时长</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 在线用户列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>在线用户列表</span>
          <div>
            <el-button type="warning" size="small" @click="cleanupExpiredUsers">
              <el-icon><Delete /></el-icon>
              清理过期
            </el-button>
            <el-button type="primary" size="small" @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <z-table
        :columns="state.columns"
        :data="state.listData"
        ref="tableRef"
        v-model:page-size="state.listQuery.page_size"
        v-model:page="state.listQuery.page"
        :total="state.total"
        :options="{ stripe: true, border: true }"
        @pagination-change="getList"
      />
    </el-card>

    <!-- 强制下线确认对话框 -->
    <el-dialog
      v-model="state.forceOfflineVisible"
      title="强制下线确认"
      width="400px"
      :close-on-click-modal="false"
    >
      <p>确定要强制用户 <strong>{{ state.selectedUser?.username }}</strong> 下线吗？</p>
      <template #footer>
        <el-button @click="state.forceOfflineVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmForceOffline">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup name="MonitorOnline">
import { h, onMounted, reactive, ref, onUnmounted } from 'vue';
import { ElMessage, ElMessageBox, ElTag, ElButton, ElAvatar } from 'element-plus';
import { User, UserFilled, Plus, Timer, Delete, Refresh, SwitchButton } from '@element-plus/icons-vue';
import { useOnlineUserApi, type OnlineUserInfo, type OnlineUserStats } from '/@/api/v1/monitor/online';

interface StateRow {
  columns: Array<any>;
  listData: Array<OnlineUserInfo>;
  total: number;
  listQuery: {
    page: number;
    page_size: number;
  };
  stats: OnlineUserStats;
  loading: boolean;
  timer: number | null;
  forceOfflineVisible: boolean;
  selectedUser: OnlineUserInfo | null;
}

const tableRef = ref();

const state = reactive<StateRow>({
  columns: [
    {
      key: 'avatar', label: '头像', width: '70', align: 'center', show: true,
      render: (row: OnlineUserInfo) => {
        return h(ElAvatar, {
          size: 40,
          src: row.avatar || undefined,
          alt: row.nickname
        }, () => row.nickname?.charAt(0) || row.username?.charAt(0) || 'U')
      }
    },
    { key: 'username', label: '用户名', minWidth: '100', align: 'center', show: true },
    { key: 'nickname', label: '昵称', minWidth: '100', align: 'center', show: true },
    { key: 'ip_address', label: 'IP地址', width: '130', align: 'center', show: true },
    { key: 'location', label: '登录地点', width: '100', align: 'center', show: true },
    { key: 'browser', label: '浏览器', width: '120', align: 'center', show: true },
    { key: 'os', label: '操作系统', width: '110', align: 'center', show: true },
    {
      key: 'is_active', label: '状态', width: '80', align: 'center', show: true,
      render: (row: OnlineUserInfo) => {
        return h(ElTag, {
          type: row.is_active ? 'success' : 'info',
          size: 'small'
        }, () => row.is_active ? '活跃' : '空闲')
      }
    },
    { key: 'login_time', label: '登录时间', width: '160', align: 'center', show: true },
    { key: 'last_activity', label: '最后活动', width: '160', align: 'center', show: true },
    { key: 'duration', label: '在线时长', width: '100', align: 'center', show: true },
    {
      key: 'action', label: '操作', width: '100', align: 'center', show: true, fixed: 'right',
      render: (row: OnlineUserInfo) => {
        return h('div', { class: 'operation-buttons' }, [
          h(ElButton, {
            type: 'danger',
            size: 'small',
            onClick: () => showForceOfflineDialog(row)
          }, {
            default: () => '下线'
          })
        ])
      }
    }
  ],
  listData: [],
  total: 0,
  listQuery: {
    page: 1,
    page_size: 20
  },
  stats: {
    total_online: 0,
    active_users: 0,
    new_today: 0,
    peak_today: 0,
    avg_duration: '0:00:00'
  },
  loading: false,
  timer: null,
  forceOfflineVisible: false,
  selectedUser: null
});

const onlineApi = useOnlineUserApi();

const getList = async () => {
  if (state.loading) return;
  
  tableRef.value?.openLoading();
  state.loading = true;
  
  try {
    const response = await onlineApi.getOnlineUsers(state.listQuery);
    if (response && response.data) {
      state.listData = response.data.items || [];
      state.total = response.data.total || 0;
    } else {
      state.listData = [];
      state.total = 0;
    }
  } catch (error) {
    console.error('获取在线用户列表失败:', error);
    ElMessage.error('获取在线用户列表失败');
    state.listData = [];
    state.total = 0;
  } finally {
    state.loading = false;
    tableRef.value?.closeLoading();
  }
};

const getStats = async () => {
  try {
    const response = await onlineApi.getOnlineStats();
    if (response && response.data) {
      state.stats = response.data;
    }
  } catch (error) {
    console.error('获取在线用户统计失败:', error);
  }
};

const refreshData = () => {
  getList();
  getStats();
};

const showForceOfflineDialog = (user: OnlineUserInfo) => {
  state.selectedUser = user;
  state.forceOfflineVisible = true;
};

const confirmForceOffline = async () => {
  if (!state.selectedUser) return;
  
  try {
    const response = await onlineApi.forceOffline(
      state.selectedUser.user_id, 
      state.selectedUser.session_id
    );
    
    if (response) {
      ElMessage.success('用户已强制下线');
      state.forceOfflineVisible = false;
      state.selectedUser = null;
      refreshData();
    }
  } catch (error) {
    console.error('强制下线失败:', error);
    ElMessage.error('强制下线失败');
  }
};

const cleanupExpiredUsers = async () => {
  try {
    await ElMessageBox.confirm('确定要清理过期的在线用户吗？', '确认清理', {
      type: 'warning'
    });
    
    const response = await onlineApi.cleanupExpiredUsers();
    if (response) {
      ElMessage.success('清理完成');
      refreshData();
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清理过期用户失败:', error);
      ElMessage.error('清理过期用户失败');
    }
  }
};

onMounted(() => {
  refreshData();
  // 每30秒自动刷新
  state.timer = window.setInterval(() => {
    refreshData();
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

.stats-card {
  height: 100px;
}

.stats-item {
  display: flex;
  align-items: center;
  height: 100%;
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  margin-right: 15px;
}

.stats-icon.online {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stats-icon.active {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stats-icon.new {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stats-icon.duration {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stats-content {
  flex: 1;
}

.stats-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stats-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.operation-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
  white-space: nowrap;
}
</style>