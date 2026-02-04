<template>
  <div class="system-operation-log-container app-container">
    <el-card>
      <div class="system-operation-log-search mb15">
        <el-input v-model="state.listQuery.username" placeholder="请输入用户名" style="max-width: 180px"></el-input>
        <el-input v-model="state.listQuery.operation" placeholder="请输入操作类型" style="max-width: 180px" class="ml10"></el-input>
        <el-select v-model="state.listQuery.method" placeholder="请求方法" style="max-width: 120px" class="ml10" clearable>
          <el-option label="GET" value="GET"></el-option>
          <el-option label="POST" value="POST"></el-option>
          <el-option label="PUT" value="PUT"></el-option>
          <el-option label="DELETE" value="DELETE"></el-option>
          <el-option label="PATCH" value="PATCH"></el-option>
        </el-select>
        <el-select v-model="state.listQuery.status" placeholder="操作状态" style="max-width: 120px" class="ml10" clearable>
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
        <el-button v-auth="'system:log:operation:list'" type="primary" class="ml10" @click="search">
          <el-icon><Search /></el-icon>
          查询
        </el-button>
        <el-button class="ml10" @click="reset">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
        <el-button v-auth="'system:log:operation:delete'" type="danger" class="ml10" @click="batchDelete" :disabled="state.selectedRows.length === 0">
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
        <el-button v-auth="'system:log:operation:clean'" type="warning" class="ml10" @click="clearLogs">
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
      title="操作日志详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-descriptions :column="2" border v-if="state.detailData">
        <el-descriptions-item label="用户名">{{ state.detailData.username || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">{{ state.detailData.operation || '-' }}</el-descriptions-item>
        <el-descriptions-item label="请求方法">
          <el-tag :type="getMethodTagType(state.detailData.method)">{{ state.detailData.method }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="操作模块">{{ state.detailData.module || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作IP">{{ state.detailData.ip || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作地点">{{ state.detailData.location || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作状态">
          <el-tag :type="state.detailData.status === 1 ? 'success' : 'danger'">
            {{ state.detailData.status === 1 ? '成功' : '失败' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="执行时间">{{ state.detailData.execution_time }}ms</el-descriptions-item>
        <el-descriptions-item label="操作时间" :span="2">{{ formatDateTime(state.detailData.operation_time) }}</el-descriptions-item>
        <el-descriptions-item label="请求URL" :span="2">{{ state.detailData.url }}</el-descriptions-item>
        <el-descriptions-item label="操作描述" :span="2">{{ state.detailData.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="用户代理" :span="2">
          <div style="word-break: break-all;">{{ state.detailData.user_agent || '-' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="请求参数" :span="2" v-if="state.detailData.request_data">
          <el-input
            type="textarea"
            :rows="6"
            :value="JSON.stringify(state.detailData.request_data, null, 2)"
            readonly
          />
        </el-descriptions-item>
        <el-descriptions-item label="错误信息" :span="2" v-if="state.detailData.error_msg">
          <el-text type="danger">{{ state.detailData.error_msg }}</el-text>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="state.detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup name="SystemOperationLog">
import {h, onMounted, reactive, ref} from 'vue';
import {ElTag, ElButton, ElMessage, ElMessageBox} from 'element-plus';
import {Search, Refresh, View, Delete} from '@element-plus/icons-vue';
import {useLogApi} from '/@/api/v1/system/log';
import {formatDateTime} from '/@/utils/formatTime';
import {auth as authFunction} from '/@/utils/authFunction';

interface TableDataRow {
  id: number;
  user_id: number;
  username: string;
  operation: string;
  method: string;
  url: string;
  ip: string;
  location: string;
  user_agent: string;
  module: string;
  description: string;
  request_data: any;
  response_data: any;
  status: number;
  error_msg: string;
  execution_time: number;
  operation_time: string;
}

interface listQueryRow {
  page: number;
  page_size: number;
  username: string;
  operation: string;
  method: string;
  module: string;
  status: number | null;
  ip: string;
  begin_time: string;
  end_time: string;
}

interface StateRow {
  columns: Array<any>;
  listData: Array<TableDataRow>;
  total: number;
  listQuery: listQueryRow;
  dateRange: string[];
  detailVisible: boolean;
  detailData: TableDataRow | null;
  selectedRows: TableDataRow[];
}

const tableRef = ref()

const state = reactive<StateRow>({
  columns: [
    {columnType: 'selection', width: '50', align: 'center', show: true},
    {key: 'username', label: '用户名', width: '120', align: 'center', show: true},
    {key: 'operation', label: '操作类型', width: '100', align: 'center', show: true},
    {
      key: 'method', label: '请求方法', width: '100', align: 'center', show: true,
      render: (row: any) => {
        return h(ElTag, {
          type: getMethodTagType(row.method),
          size: 'small'
        }, () => row.method)
      }
    },
    {key: 'module', label: '操作模块', width: '120', align: 'center', show: true},
    {key: 'ip', label: '操作IP', width: '140', align: 'center', show: true},
    {
      key: 'status', label: '操作状态', width: '100', align: 'center', show: true,
      render: (row: any) => {
        const isSuccess = row.status === 1;
        return h(ElTag, {
          type: isSuccess ? "success" : "danger",
          size: 'small'
        }, () => isSuccess ? "成功" : "失败")
      }
    },
    {key: 'execution_time', label: '执行时间', width: '100', align: 'center', show: true,
      render: (row: any) => `${row.execution_time}ms`
    },
    {key: 'operation_time', label: '操作时间', width: '180', align: 'center', show: true,
      render: (row: any) => formatDateTime(row.operation_time)
    },
    {key: 'description', label: '操作描述', width: '', align: 'center', show: true},
    {
      key: 'action', label: '操作', width: '140', align: 'center', show: true, fixed: 'right',
      render: (row: any) => {
        return h('div', { class: 'operation-buttons' }, [
          h(ElButton, {
            type: 'primary',
            size: 'small',
            onClick: () => viewDetail(row),
            style: authFunction('system:log:operation:detail') ? '' : 'display:none'
          }, {
            default: () => [h(View), '详情']
          }),
          h(ElButton, {
            type: 'danger',
            size: 'small',
            onClick: () => deleteLog(row),
            style: 'margin-left: 8px;' + (authFunction('system:log:operation:delete') ? '' : 'display:none')
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
    operation: '',
    method: '',
    module: '',
    status: null,
    ip: '',
    begin_time: '',
    end_time: '',
  },
  dateRange: [],
  detailVisible: false,
  detailData: null,
  selectedRows: []
});

const getMethodTagType = (method: string) => {
  const typeMap: Record<string, string> = {
    'GET': 'info',
    'POST': 'success',
    'PUT': 'warning',
    'DELETE': 'danger',
    'PATCH': 'primary'
  }
  return typeMap[method] || 'info'
}

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
  
  useLogApi().getOperationLogs(cleanParams)
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
      console.error('获取操作日志失败:', err)
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
    operation: '',
    method: '',
    module: '',
    status: null,
    ip: '',
    begin_time: '',
    end_time: '',
  }
  state.dateRange = []
  getList()
}

const viewDetail = (row: TableDataRow) => {
  useLogApi().getDetail(row.id, 'operation')
    .then(res => {
      state.detailData = res.data
      state.detailVisible = true
    })
    .catch((error) => {
      ElMessage.error(error.message || '获取详情失败');
    });
}

// 处理表格选择变化
const handleSelectionChange = (selection: TableDataRow[]) => {
  state.selectedRows = selection;
}

// 删除单条日志
const deleteLog = (row: TableDataRow) => {
  ElMessageBox.confirm(`确定要删除用户"${row.username}"的操作日志吗？`, '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      useLogApi().batchDeleteOperationLogs([row.id])
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
  
  ElMessageBox.confirm(`确定要删除选中的 ${state.selectedRows.length} 条操作日志吗？`, '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      const ids = state.selectedRows.map(row => row.id);
      useLogApi().batchDeleteOperationLogs(ids)
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
  ElMessageBox.prompt('请输入要保留的天数（默认保留30天）', '清理操作日志', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    inputPattern: /^\d+$/,
    inputErrorMessage: '请输入有效的天数',
    inputValue: '30'
  })
    .then(({ value }) => {
      const days = parseInt(value) || 30;
      useLogApi().clearOperationLogs(days)
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