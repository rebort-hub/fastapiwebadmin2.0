<template>
  <div class="system-role-container app-container">
    <el-card>
      <div class="system-user-search mb15">
        <el-input v-model="state.listQuery.role_name" placeholder="请输入角色名称" style="max-width: 180px"></el-input>
        <el-button v-auth="'system:role:list'" type="primary" class="ml10" @click="search">查询
        </el-button>
        <el-button v-auth="'system:role:add'" type="success" class="ml10" @click="onOpenSaveOrUpdate('save', null)">新增
        </el-button>
      </div>
      <z-table
          :columns="state.columns"
          :data="state.listData"
          ref="tableRef"
          v-model:page-size="state.listQuery.pageSize"
          v-model:page="state.listQuery.page"
          :total="state.total"
          :options="{ stripe: true, border: true }"
          @pagination-change="getList"
      />
    </el-card>
    <SaveOrUpdateRole ref="SaveOrUpdateRoleRef" @getList="getList"/>
  </div>
</template>

<script lang="ts" setup name="SystemRole">
import {h, onMounted, reactive, ref} from 'vue';
import {ElButton, ElMessage, ElMessageBox, ElTag} from 'element-plus';
import SaveOrUpdateRole from '/@/views/system/role/EditRole.vue';
import {useRoleApi} from "/@/api/v1/system/role";
import {auth as authFunction} from '/@/utils/authFunction';
import {formatDateTime} from '/@/utils/formatTime';


const SaveOrUpdateRoleRef = ref();
const tableRef = ref();
const state = reactive({
  columns: [
    {
      key: 'role_name', label: '角色名称', width: '', align: 'center', show: true,
      render: (row: any) => h(ElButton, {
        link: true,
        type: "primary",
        onClick: () => {
          onOpenSaveOrUpdate("update", row)
        }
      }, () => row.role_name)
    },
    {key: 'role_key', label: '权限字符', width: '150', align: 'center', show: true},
    {key: 'role_sort', label: '显示顺序', width: '100', align: 'center', show: true},
    {
      key: 'status', label: '角色状态', width: '100', align: 'center', show: true,
      render: (row: any) => h(ElTag, {
        type: row.status == 1 ? "success" : "info",
      }, () => row.status == 1 ? "启用" : "禁用",)
    },
    {key: 'remark', label: '备注', width: '', align: 'center', show: true},
    {
      key: 'created_at', label: '创建时间', width: '180', align: 'center', show: true,
      render: (row: any) => formatDateTime(row.created_at)
    },
    {
      label: '操作', fixed: 'right', width: '140', align: 'center',
      render: (row: any) => h("div", null, [
        h(ElButton, {
          type: "primary",
          size: "small",
          onClick: () => {
            onOpenSaveOrUpdate("update", row)
          },
          style: authFunction('system:role:edit') ? '' : 'display:none'
        }, () => '编辑'),

        h(ElButton, {
          type: "danger",
          size: "small",
          onClick: () => {
            deleted(row)
          },
          style: authFunction('system:role:delete') ? '' : 'display:none'
        }, () => '删除')
      ])
    },
  ],
  // list
  listData: [],
  tableLoading: false,
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    role_name: '',
  },
});
// 初始化表格数据
const getList = () => {
  tableRef.value.openLoading()
  useRoleApi().getList(state.listQuery)
      .then(res => {
        state.listData = res.data.rows
        state.total = res.data.rowTotal
      })
      .catch((error) => {
        ElMessage.error(error.message || '获取角色列表失败');
      })
      .finally(() => {
        tableRef.value.closeLoading()
      })
};

// 查询
const search = () => {
  state.listQuery.page = 1
  getList()
}

// 新增或修改角色
const onOpenSaveOrUpdate = (editType: string, row: any) => {
  SaveOrUpdateRoleRef.value.openDialog(editType, row);
};

// 删除角色
const deleted = (row: any) => {
  ElMessageBox.confirm('是否删除该条数据, 是否继续?', '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
      .then(() => {
        useRoleApi().delete(row.id)
            .then(() => {
              ElMessage.success('删除成功');
              getList()
            })
            .catch((error) => {
              ElMessage.error(error.message || '删除失败');
            });
      })
      .catch(() => {
      });
};

// 页面加载时
onMounted(() => {
  getList();
});

</script>
