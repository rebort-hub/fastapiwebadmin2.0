<template>
  <div class="system-menu-container app-container">
    <el-card>
      <div class="system-menu-search mb15">
        <el-input v-model="state.listQuery.menu_name" placeholder="请输入菜单名称" style="max-width: 180px"></el-input>
        <el-button v-auth="'system:menu:list'" type="primary" class="ml10" @click="getList">查询
        </el-button>
        <el-button v-auth="'system:menu:add'" type="success" class="ml10" @click="onOpenSaveOrUpdate('save', null)">新增
        </el-button>
      </div>

      <z-table
          :columns="state.columns"
          :data="state.menuList"
          ref="tableRef"
          :row-key="'id'"
          :showPage="false"
          v-model:page-size="state.listQuery.pageSize"
          v-model:page="state.listQuery.page"
          :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
          :options="{ stripe: true, border: true }"
          @pagination-change="getList"
      />

    </el-card>
    <EditMenu :menuList="state.menuList"
              :allMenuList="state.allMenuList"
              @getList="getList"
              ref="EditRef"/>
  </div>
</template>

<script lang="ts" setup name="SystemMenu">
import {h, onMounted, reactive, ref} from 'vue';
import {useMenuApi} from '/@/api/v1/system/menu';
import {RouteRecordRaw} from 'vue-router';
import {ElButton, ElMessage, ElMessageBox, ElTag} from 'element-plus';
import EditMenu from '/@/views/system/menu/EditMenu.vue';
import {auth as authFunction} from '/@/utils/authFunction';


const EditRef = ref();
const tableRef = ref();
const state = reactive({
  columns: [
    {
      key: 'menu_name', label: '菜单名称', width: '', align: 'left', show: true, render: (row: any) =>
          h(ElButton, {
            link: true,
            type: "primary",
            onClick: () => {
              onOpenSaveOrUpdate('update', row)
            }
          }, () => row.menu_name),
    },
    {key: 'path', label: '路由路径', width: '', align: 'left', show: true},
    {key: 'component', label: '组件路径', width: '', align: 'left', show: true},
    {
      key: 'perms', 
      label: '权限标识', 
      width: '', 
      align: 'left', 
      show: true,
      render: (row: any) => {
        if (!row.perms || row.perms === '0' || row.perms === 0 || row.perms === 'False') {
          return '-';
        }
        return row.perms;
      }
    },
    {key: 'component_name', label: '组件名称', width: '', align: 'left', show: true},
    {key: 'order_num', label: '排序', width: '80', align: 'center', show: true},
    {
      key: 'menu_type', 
      label: '类型', 
      width: '80', 
      align: 'center', 
      show: true,
      render: (row: any) => {
        const typeMap: any = {
          'M': { text: '目录', type: 'success' },
          'C': { text: '菜单', type: 'primary' },
          'F': { text: '按钮', type: 'warning' },
          // 兼容旧数据
          1: { text: '目录', type: 'success' },
          2: { text: '菜单', type: 'primary' },
          3: { text: '按钮', type: 'warning' },
        };
        const config = typeMap[row.menu_type] || { text: row.menu_type, type: 'info' };
        return h(ElTag, { type: config.type, size: 'small' }, () => config.text);
      }
    }, {
      label: '操作', columnType: 'string', fixed: 'right', align: 'center', width: '140',
      render: (row: any) => h("div", null, [
        h(ElButton, {
          type: "primary",
          size: "small",
          onClick: () => {
            onOpenSaveOrUpdate('update', row)
          },
          style: authFunction('system:menu:edit') ? '' : 'display:none'
        }, () => '编辑'),
        h(ElButton, {
          type: "danger",
          size: "small",
          onClick: () => {
            deleted(row)
          },
          style: authFunction('system:menu:delete') ? '' : 'display:none'
        }, () => '删除')
      ])
    },
  ],
  // list
  menuList: [],
  allMenuList: null,
  listQuery: {
    page: 1,
    pageSize: 200,
    menu_name: '',
  },
});

// 递归组装菜单
const menuAssembly = (parent_menu: Array<object>, all_menu: Array<object>) => {
  parent_menu.forEach((parent: any) => {
    all_menu.forEach((menu: any) => {
      if (menu.parent_id == parent.id) {
        parent.children = parent.children ? parent.children : [];
        parent.children.push(menu);
      }
    })
    if (parent.children) menuAssembly(parent.children, all_menu);
  })
  state.menuList = parent_menu
};

// 获取菜单列表
const getList = async () => {
  tableRef.value.openLoading()
  try {
    let res = await useMenuApi().allMenu({})
    state.allMenuList = res.data
    
    // 深拷贝数据，避免引用问题
    const allMenuData = JSON.parse(JSON.stringify(res.data))
    
    let parent_menu: any = []
    allMenuData.forEach((menu: any) => {
      if (!menu.parent_id) {
        parent_menu.push(menu)
      }
    })
    
    menuAssembly(parent_menu, allMenuData)
    
    // 强制更新 menuList，触发响应式
    state.menuList = []
    setTimeout(() => {
      state.menuList = parent_menu
    }, 0)
  } catch (error: any) {
    ElMessage.error(error.message || '获取菜单列表失败');
  } finally {
    tableRef.value.closeLoading()
  }
};
// 打开新增菜单弹窗
// const onOpenAddMenu = () => {
//   addMenuRef.value.openDialog();
// };
// 打开编辑菜单弹窗
const onOpenSaveOrUpdate = (editType: string, row: RouteRecordRaw) => {
  EditRef.value.openDialog(editType, row);
};
// 删除当前行
const deleted = (row: RouteRecordRaw) => {
  ElMessageBox.confirm('是否删除该条数据, 是否继续?', '提示', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
      .then(() => {
        useMenuApi().deleted({id: row.id})
          .then(() => {
            ElMessage.success('删除成功');
            getList(); // 刷新列表
          })
          .catch((error) => {
            ElMessage.error(error.message || '删除失败');
          });
      })
      .catch(() => {
      });
};
onMounted(() => {
  getList()
})

</script>

