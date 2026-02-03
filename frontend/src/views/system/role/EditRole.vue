<template>
  <div class="system-edit-role-container">
    <el-dialog
        draggable :title="state.editType === 'save'? `新增` : `修改`" v-model="state.isShowDialog" width="900px">
      <el-form :model="state.form" :rules="state.rules" label-width="90px" ref="formRef">
        <el-row :gutter="35">
          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
            <el-form-item label="角色名称" prop="role_name">
              <el-input v-model="state.form.role_name" placeholder="请输入角色名称" clearable></el-input>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
            <el-form-item label="权限字符" prop="role_key">
              <el-input v-model="state.form.role_key" placeholder="请输入权限字符，如：admin" clearable></el-input>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
            <el-form-item label="显示顺序">
              <el-input-number v-model="state.form.role_sort" :min="0" :max="999" controls-position="right" 
                               placeholder="请输入排序" class="w100"/>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
            <el-form-item label="角色状态">
              <el-switch v-model="state.form.status" :active-value="1" :inactive-value="0" inline-prompt
                         active-text="启" inactive-text="禁"></el-switch>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
            <el-form-item label="数据权限" prop="data_scope">
              <el-select v-model="state.form.data_scope" placeholder="请选择数据权限范围" clearable class="w100">
                <el-option
                  v-for="item in state.dataScopeOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="备注">
              <el-input v-model="state.form.remark" type="textarea" placeholder="请输入备注"
                        maxlength="500"></el-input>
            </el-form-item>
          </el-col>
          <!-- 自定义数据权限部门选择 -->
          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20" v-if="state.form.data_scope === 5">
            <el-form-item label="自定义部门" prop="dept_ids">
              <div class="custom-dept-container">
                <div class="dept-selection-panel">
                  <div class="panel-header">
                    <span class="panel-title">选择部门</span>
                    <span class="count-badge">{{ state.selectedDepts.length }}</span>
                  </div>
                  <div class="panel-body">
                    <el-input
                      v-model="state.deptFilterText"
                      placeholder="请输入部门名称搜索"
                      clearable
                      prefix-icon="Search"
                      size="small"
                      class="filter-input"
                    />
                    <el-tree ref="deptTreeRef"
                             :data="state.deptData"
                             :props="state.deptProps"
                             :filter-node-method="filterDeptNode"
                             @check="deptTreeChange"
                             :default-checked-keys="state.form.dept_ids"
                             :default-expand-all="false"
                             node-key="id"
                             show-checkbox
                             check-strictly
                             class="dept-tree"/>
                  </div>
                </div>
                <div class="selected-depts-panel">
                  <div class="panel-header">
                    <span class="panel-title">已选部门</span>
                    <span class="count-badge">{{ state.selectedDepts.length }}</span>
                  </div>
                  <div class="panel-body">
                    <div class="selected-list" v-if="state.selectedDepts.length > 0">
                      <div v-for="dept in state.selectedDepts" :key="dept.id" class="selected-item">
                        <span class="dept-name">{{ dept.dept_name }}</span>
                        <el-icon class="remove-icon" @click="removeDept(dept.id)">
                          <Close />
                        </el-icon>
                      </div>
                    </div>
                    <el-empty v-else description="请选择部门" :image-size="60" />
                  </div>
                </div>
              </div>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="菜单权限" prop="menu_ids">
              <div class="menu-permission-container">
                <!-- 左侧：可选权限 -->
                <div class="permission-panel">
                  <div class="panel-header">
                    <div class="header-left">
                      <el-checkbox v-model="state.checkAll" @change="handleCheckAllChange" :indeterminate="state.isIndeterminate">
                        可选权限
                      </el-checkbox>
                      <span class="count-badge">{{ state.totalCount }}</span>
                    </div>
                    <el-button link type="primary" size="small" @click="expandAll">
                      {{ state.isExpandAll ? '收起' : '展开' }}
                    </el-button>
                  </div>
                  <div class="panel-body">
                    <el-input
                      v-model="state.filterText"
                      placeholder="请输入关键字搜索"
                      clearable
                      prefix-icon="Search"
                      size="small"
                      class="filter-input"
                    />
                    <el-tree ref="roleTreeRef"
                             :data="state.menuData"
                             :props="state.menuProps"
                             :filter-node-method="filterNode"
                             @check="roleTreeChange"
                             :default-checked-keys="state.form.menu_ids"
                             :default-expand-all="false"
                             node-key="id"
                             show-checkbox
                             check-strictly
                             :render-after-expand="false"
                             class="menu-data-tree"/>
                  </div>
                </div>
                
                <!-- 右侧：已有权限 -->
                <div class="permission-panel">
                  <div class="panel-header">
                    <div class="header-left">
                      <span class="panel-title">已有权限</span>
                      <span class="count-badge">{{ state.selectedMenus.length }}</span>
                    </div>
                    <el-button link type="danger" size="small" @click="clearAll" :disabled="state.selectedMenus.length === 0">
                      清空
                    </el-button>
                  </div>
                  <div class="panel-body">
                    <el-input
                      v-model="state.selectedFilterText"
                      placeholder="请输入关键字搜索"
                      clearable
                      prefix-icon="Search"
                      size="small"
                      class="filter-input"
                    />
                    <div class="selected-list" v-if="filteredSelectedMenus.length > 0">
                      <div v-for="menu in filteredSelectedMenus" :key="menu.id" class="selected-item">
                        <div class="item-content">
                          <el-tag :type="getMenuTypeTag(menu.menu_type)" size="small" class="type-tag">
                            {{ getMenuTypeName(menu.menu_type) }}
                          </el-tag>
                          <span class="menu-name">{{ menu.menu_name }}</span>
                        </div>
                        <el-icon class="remove-icon" @click="removeMenu(menu.id)">
                          <Close />
                        </el-icon>
                      </div>
                    </div>
                    <el-empty v-else description="暂无数据" :image-size="80" />
                  </div>
                </div>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
				<span class="dialog-footer">
					<el-button @click="onCancel">取 消</el-button>
					<el-button type="primary" @click="saveOrUpdate">保 存</el-button>
				</span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup name="SaveOrUpdateRole">
import {reactive, ref, computed, watch} from 'vue';
import {useMenuApi} from "/@/api/v1/system/menu";
import {useRoleApi} from "/@/api/v1/system/role";
import {useDeptApi} from "/@/api/v1/system/dept";
import {usePermissionApi} from "/@/api/v1/system/permission";
import {ElMessage} from "element-plus";
import {ArrowRight, ArrowLeft, Close} from '@element-plus/icons-vue';

// 定义接口来定义对象的类型
interface MenuDataTree {
  id: number;
  menu_name: string;
  children?: MenuDataTree[];
}

interface RoleData {
  id: string | number | null;
  role_name: string;
  role_key: string;
  role_sort: number;
  data_scope: number;
  status: number;
  remark: string;
  menu_ids: Array<number>;
  dept_ids: Array<number>;
}

interface RoleState {
  isShowDialog: boolean;
  editType: any;
  form: RoleData;
  rules: Object;
  menuData: Array<MenuDataTree>;
  menuProps: {
    children: string;
    label: string;
  };
  deptData: Array<any>;
  deptProps: {
    children: string;
    label: string;
  };
  dataScopeOptions: Array<{value: number; label: string}>;
  isExpandAll: boolean;
  filterText: string;
  selectedFilterText: string;
  deptFilterText: string;
  selectedMenus: Array<any>;
  selectedDepts: Array<any>;
  checkAll: boolean;
  isIndeterminate: boolean;
  totalCount: number;
}

const emit = defineEmits(['getList'])

let createForm = () => {
  return {
    id: null,
    role_name: '',  // 角色名称
    role_key: '',   // 角色权限字符串
    role_sort: 0,   // 显示顺序
    data_scope: 1,  // 数据范围
    status: 1,      // 角色状态 1 启用，0 禁用
    remark: '',     // 备注
    menu_ids: [],   // 关联菜单ID列表
    dept_ids: [],   // 部门ID列表（自定义权限）
  }
}
const formRef = ref()
const roleTreeRef = ref()
const deptTreeRef = ref()
const state = reactive<RoleState>({
  editType: null,
  isShowDialog: false,
  form: createForm(),
  menuData: [],
  deptData: [],
  dataScopeOptions: [
    { value: 1, label: '仅本人数据' },
    { value: 2, label: '本部门数据' },
    { value: 3, label: '本部门及以下数据' },
    { value: 4, label: '全部数据' },
    { value: 5, label: '自定义数据' }
  ],
  rules: {
    role_name: [{required: true, message: '请输入角色名称', trigger: 'blur'}],
    role_key: [{required: true, message: '请输入权限字符', trigger: 'blur'}],
    data_scope: [{required: true, message: '请选择数据权限范围', trigger: 'change'}],
    menu_ids: [{
      required: true,
      type: 'array',
      min: 1,
      message: '请至少选择一个菜单权限',
      trigger: 'change'
    }],
  },
  menuProps: {
    children: 'children',
    label: 'menu_name',
  },
  deptProps: {
    children: 'children',
    label: 'dept_name',
  },
  isExpandAll: false,
  filterText: '',
  selectedFilterText: '',
  deptFilterText: '',
  selectedMenus: [],
  selectedDepts: [],
  checkAll: false,
  isIndeterminate: false,
  totalCount: 0
});

// 监听搜索框变化
watch(() => state.filterText, (val) => {
  roleTreeRef.value?.filter(val);
});

// 监听部门搜索框变化
watch(() => state.deptFilterText, (val) => {
  deptTreeRef.value?.filter(val);
});

// 计算已选菜单（用于右侧显示）
const filteredSelectedMenus = computed(() => {
  if (!state.selectedFilterText) {
    return state.selectedMenus;
  }
  return state.selectedMenus.filter(menu => 
    menu.menu_name.toLowerCase().includes(state.selectedFilterText.toLowerCase())
  );
});
// 打开弹窗
const openDialog = (editType: string, row: RoleData) => {
  getMenuData()
  getDeptData()
  state.editType = editType
  if (row) {
    state.form = JSON.parse(JSON.stringify(row));
    // 确保使用新字段名
    if (!state.form.menu_ids && row.menus) {
      state.form.menu_ids = row.menus;
    }
    if (!state.form.dept_ids && row.depts) {
      state.form.dept_ids = row.depts;
    }
  } else {
    state.form = createForm()
  }
  state.isShowDialog = true;
};
// 关闭弹窗
const closeDialog = () => {
  state.isShowDialog = false;
};
// 取消
const onCancel = () => {
  closeDialog();
};
// 更新-新增
const saveOrUpdate = () => {
  formRef.value.validate((valid: any) => {
    if (valid) {
      // 处理空字符串字段，转为null
      const formData = { ...state.form };
      if (formData.remark === '') formData.remark = null;
      
      useRoleApi().saveOrUpdate(formData)
          .then(() => {
            ElMessage.success('操作成功');
            emit('getList')
            closeDialog(); // 关闭弹窗
          })
          .catch((error) => {
            ElMessage.error(error.message || '操作失败');
          });
    }
  })
}
// 获取菜单结构数据
const getMenuData = () => {
  useMenuApi().getAllMenus()
      .then(res => {
        state.menuData = res.data;
        // 计算总数
        const countTotal = (menuList: Array<MenuDataTree>) => {
          let count = 0;
          menuList.forEach(menu => {
            count++;
            if (menu.children && menu.children.length > 0) {
              count += countTotal(menu.children);
            }
          });
          return count;
        };
        state.totalCount = countTotal(state.menuData);
        // 更新已选菜单
        updateSelectedMenus();
      })
      .catch((error) => {
        ElMessage.error(error.message || '获取菜单数据失败');
      });
}
// 获取部门数据
const getDeptData = () => {
  useDeptApi().getList()
      .then(res => {
        state.deptData = res.data || [];
        // 更新已选部门
        updateSelectedDepts();
      })
      .catch((error) => {
        ElMessage.error(error.message || '获取部门数据失败');
      });
}
// 赋值勾选的权限（使用防抖优化）
let updateTimer: any = null;
const roleTreeChange = () => {
  const checkedKeys = roleTreeRef.value.getCheckedKeys(false);
  state.form.menu_ids = checkedKeys;
  
  // 防抖更新已选菜单列表
  if (updateTimer) clearTimeout(updateTimer);
  updateTimer = setTimeout(() => {
    updateSelectedMenus();
  }, 100);
}

// 更新已选菜单列表
const updateSelectedMenus = () => {
  const selectedIds = state.form.menu_ids;
  const allMenus: any[] = [];
  
  // 递归收集所有菜单
  const collectMenus = (menuList: Array<MenuDataTree>) => {
    menuList.forEach(menu => {
      allMenus.push(menu);
      if (menu.children && menu.children.length > 0) {
        collectMenus(menu.children);
      }
    });
  };
  
  collectMenus(state.menuData);
  
  // 筛选已选中的菜单
  state.selectedMenus = allMenus.filter(menu => selectedIds.includes(menu.id));
  
  // 更新全选状态
  updateCheckAllStatus();
}

// 更新全选状态
const updateCheckAllStatus = () => {
  const total = state.totalCount;
  const selected = state.form.menu_ids.length;
  state.checkAll = selected === total && total > 0;
  state.isIndeterminate = selected > 0 && selected < total;
}

// 全选/取消全选
const handleCheckAllChange = (val: boolean) => {
  if (val) {
    // 全选：收集所有菜单ID
    const allIds: number[] = [];
    const collectIds = (menuList: Array<MenuDataTree>) => {
      menuList.forEach(menu => {
        allIds.push(menu.id);
        if (menu.children && menu.children.length > 0) {
          collectIds(menu.children);
        }
      });
    };
    collectIds(state.menuData);
    state.form.menu_ids = allIds;
    roleTreeRef.value?.setCheckedKeys(allIds);
  } else {
    // 取消全选
    state.form.menu_ids = [];
    roleTreeRef.value?.setCheckedKeys([]);
  }
  updateSelectedMenus();
}

// 展开/收起全部
const expandAll = () => {
  state.isExpandAll = !state.isExpandAll;
  const tree = roleTreeRef.value;
  if (!tree) return;
  
  // 使用更高效的方式：直接设置节点展开状态
  if (state.isExpandAll) {
    // 展开所有节点
    const expandNodes = (nodes: any[]) => {
      nodes.forEach(node => {
        tree.store.nodesMap[node.id].expanded = true;
        if (node.children && node.children.length > 0) {
          expandNodes(node.children);
        }
      });
    };
    expandNodes(state.menuData);
  } else {
    // 收起所有节点
    Object.keys(tree.store.nodesMap).forEach(key => {
      tree.store.nodesMap[key].expanded = false;
    });
  }
}

// 过滤节点
const filterNode = (value: string, data: any) => {
  if (!value) return true;
  return data.menu_name.toLowerCase().includes(value.toLowerCase());
}

// 过滤部门节点
const filterDeptNode = (value: string, data: any) => {
  if (!value) return true;
  return data.dept_name.toLowerCase().includes(value.toLowerCase());
}

// 部门树变化
const deptTreeChange = () => {
  const checkedKeys = deptTreeRef.value.getCheckedKeys(false);
  state.form.dept_ids = checkedKeys;
  updateSelectedDepts();
}

// 更新已选部门列表
const updateSelectedDepts = () => {
  const selectedIds = state.form.dept_ids || [];
  const allDepts: any[] = [];
  
  // 递归收集所有部门
  const collectDepts = (deptList: Array<any>) => {
    deptList.forEach(dept => {
      allDepts.push(dept);
      if (dept.children && dept.children.length > 0) {
        collectDepts(dept.children);
      }
    });
  };
  
  collectDepts(state.deptData);
  
  // 筛选已选中的部门
  state.selectedDepts = allDepts.filter(dept => selectedIds.includes(dept.id));
}

// 移除单个部门
const removeDept = (deptId: number) => {
  state.form.dept_ids = state.form.dept_ids.filter(id => id !== deptId);
  deptTreeRef.value?.setCheckedKeys(state.form.dept_ids);
  updateSelectedDepts();
}

// 移除单个菜单
const removeMenu = (menuId: number) => {
  state.form.menu_ids = state.form.menu_ids.filter(id => id !== menuId);
  roleTreeRef.value?.setCheckedKeys(state.form.menu_ids);
  updateSelectedMenus();
}

// 清空所有
const clearAll = () => {
  state.form.menu_ids = [];
  roleTreeRef.value?.setCheckedKeys([]);
  updateSelectedMenus();
}

// 获取菜单类型名称
const getMenuTypeName = (type: string) => {
  const typeMap: any = {
    'M': '目录',
    'C': '菜单',
    'F': '按钮'
  };
  return typeMap[type] || type;
}

// 获取菜单类型标签颜色
const getMenuTypeTag = (type: string) => {
  const tagMap: any = {
    'M': 'warning',
    'C': 'success',
    'F': 'info'
  };
  return tagMap[type] || '';
}

defineExpose({
  openDialog,

})
</script>

<style scoped lang="scss">
.system-edit-role-container {
  // 菜单权限容器 - 简洁布局
  .menu-permission-container {
    display: flex;
    gap: 12px;
    align-items: stretch;
    height: 420px;
    
    // 左右面板
    .permission-panel {
      width: 350px;
      flex: 1;
      min-width: 350px;
      display: flex;
      flex-direction: column;
      border: 2px solid var(--el-border-color);
      border-radius: 8px;
      background-color: var(--el-bg-color);
      overflow: hidden;
      
      .panel-header {
        flex-shrink: 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 12px;
        background-color: var(--el-fill-color-light);
        border-bottom: 1px solid var(--el-border-color-lighter);
        
        .header-left {
          display: flex;
          align-items: center;
          gap: 8px;
          min-width: 0;
          
          .panel-title {
            font-size: 14px;
            font-weight: 500;
            color: var(--el-text-color-primary);
          }
          
          .count-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 20px;
            height: 20px;
            padding: 0 6px;
            font-size: 12px;
            color: var(--el-color-primary);
            background-color: var(--el-color-primary-light-9);
            border-radius: 10px;
            flex-shrink: 0;
          }
        }
      }
      
      .panel-body {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        min-height: 0;
        
        .filter-input {
          flex-shrink: 0;
          margin: 10px;
          width: calc(100% - 20px);
        }
        
        .menu-data-tree {
          flex: 1;
          padding: 0 10px 10px;
          overflow-y: auto;
          overflow-x: hidden;
          min-height: 0;
          
          &::-webkit-scrollbar {
            width: 6px;
          }
          
          &::-webkit-scrollbar-thumb {
            background-color: var(--el-text-color-placeholder);
            border-radius: 3px;
            
            &:hover {
              background-color: var(--el-text-color-secondary);
            }
          }
          
          &::-webkit-scrollbar-track {
            background-color: transparent;
          }
        }
        
        .selected-list {
          flex: 1;
          padding: 0 10px 10px;
          overflow-y: auto;
          overflow-x: hidden;
          min-height: 0;
          
          &::-webkit-scrollbar {
            width: 6px;
          }
          
          &::-webkit-scrollbar-thumb {
            background-color: var(--el-text-color-placeholder);
            border-radius: 3px;
            
            &:hover {
              background-color: var(--el-text-color-secondary);
            }
          }
          
          &::-webkit-scrollbar-track {
            background-color: transparent;
          }
          
          .selected-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 10px;
            margin-bottom: 6px;
            background-color: var(--el-fill-color);
            border-radius: var(--el-border-radius-base);
            transition: all 0.2s;
            
            &:hover {
              background-color: var(--el-fill-color-dark);
              
              .remove-icon {
                opacity: 1;
              }
            }
            
            .item-content {
              flex: 1;
              display: flex;
              align-items: center;
              gap: 8px;
              min-width: 0;
              
              .type-tag {
                flex-shrink: 0;
              }
              
              .menu-name {
                flex: 1;
                font-size: 13px;
                color: var(--el-text-color-primary);
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
              }
            }
            
            .remove-icon {
              flex-shrink: 0;
              font-size: 16px;
              color: var(--el-text-color-secondary);
              cursor: pointer;
              opacity: 0.6;
              transition: all 0.2s;
              
              &:hover {
                color: var(--el-color-danger);
                opacity: 1;
              }
            }
          }
        }
      }
    }
  }
  
  // 自定义部门选择容器
  .custom-dept-container {
    display: flex;
    gap: 12px;
    align-items: stretch;
    height: 420px;
    
    .dept-selection-panel {
      width: 350px;
      flex: 1;
      min-width: 350px;
      display: flex;
      flex-direction: column;
      border: 2px solid var(--el-border-color);
      border-radius: 8px;
      background-color: var(--el-bg-color);
      overflow: hidden;
      
      .panel-header {
        flex-shrink: 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 12px;
        background-color: var(--el-fill-color-light);
        border-bottom: 1px solid var(--el-border-color-lighter);
        
        .panel-title {
          font-size: 14px;
          font-weight: 500;
          color: var(--el-text-color-primary);
        }
        
        .count-badge {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          min-width: 20px;
          height: 20px;
          padding: 0 6px;
          font-size: 12px;
          color: var(--el-color-primary);
          background-color: var(--el-color-primary-light-9);
          border-radius: 10px;
          flex-shrink: 0;
        }
      }
      
      .panel-body {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        min-height: 0;
        
        .filter-input {
          flex-shrink: 0;
          margin: 10px;
          width: calc(100% - 20px);
        }
        
        .dept-tree {
          flex: 1;
          padding: 0 10px 10px;
          overflow-y: auto;
          overflow-x: hidden;
          min-height: 0;
          
          &::-webkit-scrollbar {
            width: 6px;
          }
          
          &::-webkit-scrollbar-thumb {
            background-color: var(--el-text-color-placeholder);
            border-radius: 3px;
            
            &:hover {
              background-color: var(--el-text-color-secondary);
            }
          }
          
          &::-webkit-scrollbar-track {
            background-color: transparent;
          }
        }
      }
    }
    
    .selected-depts-panel {
      flex: 1;
      min-width: 350px;
      display: flex;
      flex-direction: column;
      border: 2px solid var(--el-border-color);
      border-radius: 8px;
      background-color: var(--el-bg-color);
      overflow: hidden;
      
      .panel-header {
        flex-shrink: 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 12px;
        background-color: var(--el-fill-color-light);
        border-bottom: 1px solid var(--el-border-color-lighter);
        
        .panel-title {
          font-size: 14px;
          font-weight: 500;
          color: var(--el-text-color-primary);
        }
        
        .count-badge {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          min-width: 20px;
          height: 20px;
          padding: 0 6px;
          font-size: 12px;
          color: var(--el-color-primary);
          background-color: var(--el-color-primary-light-9);
          border-radius: 10px;
          flex-shrink: 0;
        }
      }
      
      .panel-body {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        min-height: 0;
        
        .selected-list {
          flex: 1;
          padding: 10px;
          overflow-y: auto;
          overflow-x: hidden;
          min-height: 0;
          
          &::-webkit-scrollbar {
            width: 6px;
          }
          
          &::-webkit-scrollbar-thumb {
            background-color: var(--el-text-color-placeholder);
            border-radius: 3px;
            
            &:hover {
              background-color: var(--el-text-color-secondary);
            }
          }
          
          &::-webkit-scrollbar-track {
            background-color: transparent;
          }
          
          .selected-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 10px;
            margin-bottom: 6px;
            background-color: var(--el-fill-color);
            border-radius: var(--el-border-radius-base);
            transition: all 0.2s;
            
            &:hover {
              background-color: var(--el-fill-color-dark);
              
              .remove-icon {
                opacity: 1;
              }
            }
            
            .dept-name {
              flex: 1;
              font-size: 13px;
              color: var(--el-text-color-primary);
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
            
            .remove-icon {
              flex-shrink: 0;
              font-size: 16px;
              color: var(--el-text-color-secondary);
              cursor: pointer;
              opacity: 0.6;
              transition: all 0.2s;
              
              &:hover {
                color: var(--el-color-danger);
                opacity: 1;
              }
            }
          }
        }
      }
    }
  }
}
</style>
