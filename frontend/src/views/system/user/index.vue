<template>
  <div class="system-user-container app-container">
    <el-card>
      <div class="system-user-search mb15">
        <el-input v-model="state.listQuery.username" placeholder="请输入用户名称" style="max-width: 180px"></el-input>
        <el-button v-auth="'system:user:list'" type="primary" class="ml10" @click="search">查询
        </el-button>
        <el-button v-auth="'system:user:add'" type="success" class="ml10" @click="onOpenSaveOrUpdate('save', null)">
          新增
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
    <SaveOrUpdateUser @getList="getList" :roleList="state.roleList" ref="SaveOrUpdateUserRef"/>
  </div>
</template>

<script lang="ts" setup name="SystemUser">
import {h, onMounted, reactive, ref} from 'vue';
import {ElButton, ElMessage, ElMessageBox, ElTag} from 'element-plus';
import SaveOrUpdateUser from '/@/views/system/user/EditUser.vue';
import {useUserApi} from '/@/api/v1/system/user';
import {useRoleApi} from "/@/api/v1/system/role";
import {auth as authFunction} from '/@/utils/authFunction';
import {formatDateTime} from '/@/utils/formatTime';

// 定义接口来定义对象的类型
interface TableDataRow {
  id: number;
  username: string;
  email: string;
  roles: string;
  status: boolean;
  nickname: string;
  user_type: number;
  created_by: number;
  updated_by: number;
  creation_date: string;
  updation_date: string;
}

interface listQueryRow {
  page: number;
  pageSize: number;
  username: string;

}

interface StateRow {
  columns: Array<any>;
  fieldData: Array<any>;
  listData: Array<TableDataRow>;
  total: number;
  listQuery: listQueryRow;
  roleList: Array<any>;
  roleQuery: listQueryRow;
}


const SaveOrUpdateUserRef = ref()
const tableRef = ref()

const state = reactive<StateRow>({
  columns: [
    {
      key: 'username', label: '账户名称', width: '', align: 'center', show: true,
      render: (row: any) => h(ElButton, {
        link: true,
        type: "primary",
        onClick: () => {
          onOpenSaveOrUpdate("update", row)
        }
      }, () => row.username)
    },
    {key: 'nickname', label: '用户昵称', width: '', align: 'center', show: true},
    {
      key: 'roles', label: '关联角色', width: '', align: 'center', show: true,
      render: (row: any) => handleRoles(row.roles)
    },
    {key: 'dept_name', label: '所属部门', width: '150', align: 'center', show: true},
    {key: 'email', label: '邮箱', width: '', align: 'center', show: true},
    {
      key: 'status', label: '用户状态', width: '', align: 'center', show: true,
      render: (row: any) => h(ElTag, {
        type: row.status ? "success" : "info",
      }, () => row.status ? "启用" : "禁用",)
    },
    {key: 'remarks', label: '备注', width: '', align: 'center', show: true},
    {
      key: 'created_at', label: '创建时间', width: '180', align: 'center', show: true,
      render: (row: any) => formatDateTime(row.created_at)
    },
    {
      label: '操作', 
      columnType: 'string', 
      fixed: 'right', 
      align: 'center', 
      width: '280',
      render: (row: any) => h("div", null, [
        h(ElButton, {
          type: "primary",
          size: "small",
          onClick: () => {
            onOpenSaveOrUpdate('update', row)
          },
          style: authFunction('system:user:edit') ? '' : 'display:none'
        }, () => '编辑'),
        h(ElButton, {
          type: row.status ? "warning" : "success",
          size: "small",
          onClick: () => {
            toggleStatus(row)
          },
          style: authFunction('system:user:status') ? '' : 'display:none'
        }, () => row.status ? '禁用' : '启用'),
        h(ElButton, {
          type: "info",
          size: "small",
          onClick: () => {
            resetPassword(row)
          },
          style: authFunction('system:user:reset-password') ? '' : 'display:none'
        }, () => '重置密码'),
        h(ElButton, {
          type: "danger",
          size: "small",
          onClick: () => {
            deleted(row)
          },
          style: authFunction('system:user:delete') ? '' : 'display:none'
        }, () => '删除')
      ])
    },
  ],
  // list
  listData: [],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    username: '',
  },
  //rule
  roleList: [],
  roleQuery: {
    page: 1,
    pageSize: 100,
  }
});
// 获取用户数据
const getList = () => {
  tableRef.value.openLoading()
  useUserApi().getList(state.listQuery)
    .then(res => {
      state.listData = res.data.rows
      state.total = res.data.rowTotal
    })
    .catch((error) => {
      ElMessage.error(error.message || '获取用户列表失败');
    })
    .finally(() => {
      tableRef.value.closeLoading()
    })
};

const getRolesList = () => {
  useRoleApi().getList(state.roleQuery)
    .then((res: any) => {
      state.roleList = res.data.rows
    })
    .catch((error) => {
      ElMessage.error(error.message || '获取角色列表失败');
    });
};

// 查询
const search = () => {
  state.listQuery.page = 1
  getList()
}

// 新增或修改用户
const onOpenSaveOrUpdate = (editType: string, row?: TableDataRow) => {
  SaveOrUpdateUserRef.value.openDialog(editType, row);
};

// 删除用户
const deleted = (row: TableDataRow) => {
  ElMessageBox.confirm('是否删除该条数据, 是否继续?', '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      useUserApi().deleted({id: row.id})
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

// 启用/禁用用户
const toggleStatus = (row: TableDataRow) => {
  const action = row.status ? '禁用' : '启用';
  ElMessageBox.confirm(`确定要${action}该用户吗？`, '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      const updatedRow = {
        ...row,
        status: row.status ? 0 : 1
      };
      useUserApi().saveOrUpdate(updatedRow)
        .then(() => {
          ElMessage.success(`${action}成功`);
          getList()
        })
        .catch((error) => {
          ElMessage.error(error.message || `${action}失败`);
        });
    })
    .catch(() => {
    });
};

// 重置密码
const resetPassword = (row: TableDataRow) => {
  ElMessageBox.confirm(`确定要重置用户"${row.nickname}"的密码吗？密码将重置为：123456`, '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      useUserApi().adminResetPassword({id: row.id})
        .then(() => {
          ElMessage.success('密码已重置为：123456');
        })
        .catch((error) => {
          ElMessage.error(error.message || '重置密码失败');
        });
    })
    .catch(() => {
    });
};

// 处理角色名称
const handleRoles = (roles: any) => {
  let roleTagList: any[] = []
  // 优先使用role_names（新架构），如果没有则使用role_ids查找
  if (Array.isArray(roles)) {
    // 如果是字符串数组（role_names）
    if (roles.length > 0 && typeof roles[0] === 'string') {
      roles.forEach((roleName: string) => {
        roleTagList.push(h(ElTag, null, () => roleName))
      })
    }
    // 如果是数字数组（role_ids）
    else {
      roles.forEach((roleId: any) => {
        let roleName = state.roleList.find(e => e.id == roleId)?.name
        if (roleName) {
          roleTagList.push(h(ElTag, null, () => roleName))
        }
      })
    }
  }
  return h('div', null, roleTagList)
}
// 页面加载时
onMounted(() => {
  getList();
  getRolesList()
});

</script>
