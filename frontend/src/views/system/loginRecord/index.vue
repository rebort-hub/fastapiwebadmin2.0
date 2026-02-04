<template>
  <div class="system-login-record-container app-container">
    <el-card>
      <div class="system-login-record-search mb15">
        <el-input v-model="state.listQuery.username" placeholder="请输入用户名" style="max-width: 180px"></el-input>
        <el-input v-model="state.listQuery.ip" placeholder="请输入登录IP" style="max-width: 180px" class="ml10"></el-input>
        <el-select v-model="state.listQuery.status" placeholder="登录状态" style="max-width: 120px" class="ml10" clearable>
          <el-option label="成功" :value="1"></el-option>
          <el-option label="失败" :value="0"></el-option>
        </el-select>
        <el-date-picker
          v-model="state.dateRange"
          type="datetimerange"
          range-separator="至"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DD HH:mm:ss"
          class="ml10"
          style="width: 350px"
        />
        <el-button v-auth="'system:log:login:list'" type="primary" class="ml10" @click="search">
          <el-icon><Search /></el-icon>
          查询
        </el-button>
        <el-button class="ml10" @click="reset">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
        <el-button v-auth="'system:log:login:delete'" type="danger" class="ml10" @click="batchDelete" :disabled="state.selectedRows.length === 0">
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
        <el-button v-auth="'system:log:login:clean'" type="warning" class="ml10" @click="clearLogs">
          <el-icon><Delete /></el-icon>
          清理日志
        </el-button>
      </div>
      <z-table
          :columns="state.columns"
          :data="state.listData"
          ref="tableRef"
          v-model:page-size="state.listQuery.page_size"
          v-model:page="state.listQuery.page"
          :total="state.total"
          :options="{ stripe: true, border: true }"
          @pagination-change="getList"
          @selection-change="handleSelectionChange"
      />
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="state.detailVisible"
      title="登录日志详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-descriptions :column="2" border v-if="state.detailData">
        <el-descriptions-item label="用户名">{{ state.detailData.username || '-' }}</el-descriptions-item>
        <el-descriptions-item label="登录类型">{{ state.detailData.login_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="登录IP">{{ state.detailData.ip || '-' }}</el-descriptions-item>
        <el-descriptions-item label="登录地点">{{ state.detailData.location || '-' }}</el-descriptions-item>
        <el-descriptions-item label="浏览器">{{ state.detailData.browser || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作系统">{{ state.detailData.os || '-' }}</el-descriptions-item>
        <el-descriptions-item label="登录状态">
          <el-tag :type="state.detailData.status === 1 ? 'success' : 'danger'">
            {{ state.detailData.status === 1 ? '成功' : '失败' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="登录时间">{{ formatDateTime(state.detailData.login_time) }}</el-descriptions-item>
        <el-descriptions-item label="退出时间" v-if="state.detailData.logout_time">{{ formatDateTime(state.detailData.logout_time) }}</el-descriptions-item>
        <el-descriptions-item label="登录信息" :span="2">{{ state.detailData.message || '-' }}</el-descriptions-item>
        <el-descriptions-item label="用户代理" :span="2">
          <div style="word-break: break-all;">{{ state.detailData.user_agent || '-' }}</div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="state.detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup name="SystemLoginRecord">
import {h, onMounted, reactive, ref} from 'vue';
import {ElTag, ElButton, ElMessage, ElMessageBox} from 'element-plus';
import {Search, Refresh, Delete, View} from '@element-plus/icons-vue';
import {useLogApi} from '/@/api/v1/system/log';
import {formatDateTime} from '/@/utils/formatTime';
import {auth as authFunction} from '/@/utils/authFunction';

interface TableDataRow {
  id: number;
  user_id: number;
  username: string;
  login_type: string;
  ip: string;
  location: string;
  user_agent: string;
  browser: string;
  os: string;
  status: number;
  message: string;
  login_time: string;
  logout_time: string;
}

interface listQueryRow {
  page: number;
  page_size: number;
  username: string;
  ip: string;
  status: number | null;
  begin_time: string;
  end_time: string;
}

interface StateRow {
  columns: Array<any>;
  listData: Array<TableDataRow>;
  total: number;
  listQuery: listQueryRow;
  dateRange: string[];
  selectedRows: TableDataRow[];
  detailVisible: boolean;
  detailData: TableDataRow | null;
}

const tableRef = ref()

const state = reactive<StateRow>({
  columns: [
    {columnType: 'selection', width: '50', align: 'center', show: true},
    {key: 'username', label: '用户名', width: '120', align: 'center', show: true},
    {key: 'ip', label: '登录IP', width: '140', align: 'center', show: true},
    {key: 'location', label: '登录地点', width: '120', align: 'center', show: true},
    {key: 'browser', label: '浏览器', width: '150', align: 'center', show: true},
    {key: 'os', label: '操作系统', width: '150', align: 'center', show: true},
    {
      key: 'status', label: '登录状态', width: '100', align: 'center', show: true,
      render: (row: any) => {
        const isSuccess = row.status === 1;
        return h(ElTag, {
          type: isSuccess ? "success" : "danger",
        }, () => isSuccess ? "成功" : "失败")
      }
    },
    {key: 'login_time', label: '登录时间', width: '180', align: 'center', show: true,
      render: (row: any) => formatDateTime(row.login_time)
    },
    {key: 'logout_time', label: '退出时间', width: '180', align: 'center', show: true,
      render: (row: any) => formatDateTime(row.logout_time)
    },
    {key: 'message', label: '登录信息', width: '', align: 'center', show: true},
    {
      key: 'action', label: '操作', width: '140', align: 'center', show: true, fixed: 'right',
      render: (row: any) => {
        return h('div', { class: 'operation-buttons' }, [
          h(ElButton, {
            type: 'primary',
            size: 'small',
            onClick: () => viewDetail(row),
            style: authFunction('system:log:login:detail') ? '' : 'display:none'
          }, {
            default: () => [h(View), '详情']
          }),
          h(ElButton, {
            type: 'danger',
            size: 'small',
            onClick: () => deleteLog(row),
            style: 'margin-left: 8px;' + (authFunction('system:log:login:delete') ? '' : 'display:none')
          }, {
            default: () => [h(Delete), '删除']
          })
        ])
      }
    }
  ],
  listData: [],
  total: 0,
  listQuery: {
    page: 1,
    page_size: 20,
    username: '',
    ip: '',
    status: null,
    begin_time: '',
    end_time: '',
  },
  dateRange: [],
  selectedRows: [],
  detailVisible: false,
  detailData: null
});

const getList = () => {
  tableRef.value.openLoading()
  
  // 处理时间范围
  if (state.dateRange && state.dateRange.length === 2) {
    state.listQuery.begin_time = state.dateRange[0];
    state.listQuery.end_time = state.dateRange[1];
  } else {
    state.listQuery.begin_time = '';
    state.listQuery.end_time = '';
  }
  
  // 清理空参数，确保空查询条件能查询所有数据
  const cleanParams = Object.fromEntries(
    Object.entries(state.listQuery).filter(([_, value]) => value !== '' && value !== null && value !== undefined)
  );
  
  useLogApi().getLoginLogs(cleanParams)
    .then(res => {
      if (res && res.data) {
        state.listData = res.data.items || []
        state.total = res.data.total || 0
      } else {
        state.listData = []
        state.total = 0
      }
    })
    .catch(err => {
      console.error('获取登录日志失败:', err)
      state.listData = []
      state.total = 0
    })
    .finally(() => {
      tableRef.value.closeLoading()
    })
};

const search = () => {
  state.listQuery.page = 1
  getList()
}

const reset = () => {
  state.listQuery = {
    page: 1,
    page_size: 20,
    username: '',
    ip: '',
    status: null,
    begin_time: '',
    end_time: '',
  }
  state.dateRange = []
  getList()
}

// 处理表格选择变化
const handleSelectionChange = (selection: TableDataRow[]) => {
  state.selectedRows = selection;
}

// 查看详情
const viewDetail = (row: TableDataRow) => {
  useLogApi().getDetail(row.id, 'login')
    .then(res => {
      state.detailData = res.data
      state.detailVisible = true
    })
    .catch((error) => {
      ElMessage.error(error.message || '获取详情失败');
    });
}

// 删除单条日志
const deleteLog = (row: TableDataRow) => {
  ElMessageBox.confirm(`确定要删除用户"${row.username}"的登录日志吗？`, '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      useLogApi().batchDeleteLoginLogs([row.id])
        .then(() => {
          ElMessage.success('删除成功');
          getList();
        })
        .catch((error) => {
          ElMessage.error(error.message || '删除失败');
        });
    })
    .catch(() => {});
}

// 批量删除
const batchDelete = () => {
  if (state.selectedRows.length === 0) {
    ElMessage.warning('请选择要删除的记录');
    return;
  }
  
  ElMessageBox.confirm(`确定要删除选中的 ${state.selectedRows.length} 条登录日志吗？`, '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      const ids = state.selectedRows.map(row => row.id);
      useLogApi().batchDeleteLoginLogs(ids)
        .then(() => {
          ElMessage.success('删除成功');
          state.selectedRows = [];
          getList();
        })
        .catch((error) => {
          ElMessage.error(error.message || '删除失败');
        });
    })
    .catch(() => {});
}

// 清理日志
const clearLogs = () => {
  ElMessageBox.prompt('请输入要保留的天数（默认保留90天）', '清理登录日志', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    inputPattern: /^\d+$/,
    inputErrorMessage: '请输入有效的天数',
    inputValue: '90'
  })
    .then(({ value }) => {
      const days = parseInt(value) || 90;
      useLogApi().clearLoginLogs(days)
        .then((res) => {
          const count = res.data?.deleted_count || 0;
          ElMessage.success(`清理完成，删除了 ${count} 条记录`);
          getList();
        })
        .catch((error) => {
          ElMessage.error(error.message || '清理失败');
        });
    })
    .catch(() => {});
}

onMounted(() => {
  getList();
});

</script>

<style scoped>
.operation-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
  white-space: nowrap;
}
</style>
