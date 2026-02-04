<template>
  <div class="system-permission-container app-container">
    <el-card>
      <div class="system-permission-search mb15">
        <el-input v-model="state.listQuery.permission_name" placeholder="请输入权限名称" style="max-width: 180px"></el-input>
        <el-select v-model="state.listQuery.permission_type" placeholder="权限类型" clearable style="max-width: 150px; margin-left: 10px">
          <el-option label="菜单权限" :value="1"></el-option>
          <el-option label="按钮权限" :value="2"></el-option>
          <el-option label="数据权限" :value="3"></el-option>
          <el-option label="API权限" :value="4"></el-option>
        </el-select>
        <el-button v-auth="'system:permission:list'" type="primary" class="ml10" @click="getList">查询</el-button>
        <el-button v-auth="'system:permission:add'" type="success" class="ml10" @click="onOpenEdit('add', null)">新增权限</el-button>
      </div>

      <z-table
          :columns="state.columns"
          :data="state.permissionList"
          ref="tableRef"
          :showPage="true"
          v-model:page-size="state.listQuery.pageSize"
          v-model:page="state.listQuery.page"
          :total="state.total"
          :options="{ stripe: true, border: true }"
          @pagination-change="getList"
      />
    </el-card>

    <EditPermission
        ref="EditRef"
        @getList="getList"
    />
  </div>
</template>

<script lang="ts" setup name="SystemPermission">
import {h, onMounted, reactive, ref} from 'vue';
import {ElButton, ElMessage, ElMessageBox, ElTag} from 'element-plus';
import EditPermission from '/@/views/system/permission/EditPermission.vue';
import {usePermissionApi} from '/@/api/v1/system/permission';
import {auth as authFunction} from '/@/utils/authFunction';

const EditRef = ref();
const tableRef = ref();

const state = reactive({
  columns: [
    {
      key: 'permission_code',
      label: '权限编码',
      width: '180',
      align: 'left',
      show: true,
      render: (row: any) =>
          h(ElButton, {
            link: true,
            type: "primary",
            onClick: () => {
              onOpenEdit('edit', row)
            }
          }, () => row.permission_code),
    },
    {key: 'permission_name', label: '权限名称', width: '150', align: 'left', show: true},
    {
      key: 'permission_type',
      label: '权限类型',
      width: '100',
      align: 'center',
      show: true,
      render: (row: any) => {
        const typeMap: any = {
          1: {text: '菜单权限', type: 'success'},
          2: {text: '按钮权限', type: 'primary'},
          3: {text: '数据权限', type: 'warning'},
          4: {text: 'API权限', type: 'info'}
        };
        const config = typeMap[row.permission_type] || {text: row.permission_type, type: 'info'};
        return h(ElTag, {type: config.type, size: 'small'}, () => config.text);
      }
    },
    {key: 'resource_type', label: '资源类型', width: '120', align: 'left', show: true},
    {
      key: 'status',
      label: '状态',
      width: '80',
      align: 'center',
      show: true,
      render: (row: any) => {
        return h(ElTag, {
          type: row.status === 1 ? 'success' : 'danger',
          size: 'small'
        }, () => row.status === 1 ? '启用' : '禁用');
      }
    },
    {key: 'sort', label: '排序', width: '80', align: 'center', show: true},
    {key: 'description', label: '描述', width: '', align: 'left', show: true},
    {
      label: '操作',
      columnType: 'string',
      fixed: 'right',
      align: 'center',
      width: '140',
      render: (row: any) => {
        const buttons = [];
        
        // 编辑按钮 - 需要编辑权限
        buttons.push(h(ElButton, {
          type: "primary",
          size: "small",
          onClick: () => {
            onOpenEdit('edit', row)
          },
          style: authFunction('system:permission:edit') ? '' : 'display:none'
        }, () => '编辑'));
        
        // 删除按钮 - 需要删除权限
        buttons.push(h(ElButton, {
          type: "danger",
          size: "small",
          onClick: () => {
            deleted(row)
          },
          style: authFunction('system:permission:delete') ? '' : 'display:none'
        }, () => '删除'));
        
        return h("div", null, buttons);
      }
    },
  ],
  permissionList: [],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    permission_name: '',
    permission_type: null,
  },
});

// 获取权限列表
const getList = async () => {
  tableRef.value.openLoading()
  try {
    // 处理查询参数，过滤空值
    const params = {
      page: state.listQuery.page,
      page_size: state.listQuery.pageSize,
      permission_name: state.listQuery.permission_name || undefined,
      permission_type: state.listQuery.permission_type || undefined,
    }
    
    let res = await usePermissionApi().getList(params)
    state.permissionList = res.data?.items || []
    state.total = res.data?.total || 0
  } catch (error) {
    console.error('获取权限列表失败:', error)
    ElMessage.error('获取权限列表失败')
  } finally {
    tableRef.value.closeLoading()
  }
};

// 打开编辑弹窗
const onOpenEdit = (editType: string, row: any) => {
  EditRef.value.openDialog(editType, row);
};

// 删除权限
const deleted = (row: any) => {
  ElMessageBox.confirm('删除后将无法恢复，是否继续?', '提示', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
      .then(async () => {
        try {
          await usePermissionApi().delete(row.id)
          ElMessage.success('删除成功');
          getList();
        } catch (error) {
          console.error('删除失败:', error)
          ElMessage.error('删除失败')
        }
      })
      .catch(() => {
      });
};

onMounted(() => {
  getList()
})
</script>

<style scoped lang="scss">
.system-permission-container {
  .system-permission-search {
    display: flex;
    align-items: center;
  }
}
</style>
