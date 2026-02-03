<template>
  <div class="system-edit-menu-container">
    <el-dialog
        draggable
        :title="state.editType === 'save'? '新增菜单' : '修改菜单'"
        v-model="state.isShowDialog"
        width="769px">
      <el-form :model="state.form" :rules="state.rules" size="default" label-width="80px" :key="state.form.menu_type" ref="formRef">
        <el-row :gutter="35">
          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="上级菜单" prop="parent_id">
              <el-select v-model="state.form.parent_id" clearable placeholder="Select">
                <el-option :value="0" label="根目录"></el-option>
                <el-option
                    v-for="item in allMenuList"
                    :key="item.id"
                    :label="item.menu_name"
                    :value="item.id"
                >
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="菜单类型" prop="menu_type">
              <el-radio-group v-model="state.form.menu_type">
                <el-radio label="M">目录</el-radio>
                <el-radio label="C">菜单</el-radio>
                <el-radio label="F">按钮</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
            <el-form-item label="菜单名称" prop="menu_name">
              <el-input v-model="state.form.menu_name" placeholder="请输入菜单名称" clearable></el-input>
            </el-form-item>
          </el-col>
          
          <!-- 按钮类型的字段 -->
          <template v-if="state.form.menu_type === 'F'">
            <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
              <el-form-item label="权限标识" prop="perms">
                <el-input v-model="state.form.perms" placeholder="如：system:user:add" clearable></el-input>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
              <el-form-item label="菜单排序">
                <el-input-number v-model="state.form.order_num" controls-position="right" placeholder="请输入排序" class="w100"/>
              </el-form-item>
            </el-col>
          </template>
          
          <!-- 目录和菜单类型的字段 -->
          <template v-if="state.form.menu_type === 'C' || state.form.menu_type === 'M'">
            <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
              <el-form-item label="组件名称" prop="component_name">
                <el-input v-model="state.form.component_name" placeholder="路由中的 name 值" clearable></el-input>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
              <el-form-item label="路由路径" prop="path">
                <el-input v-model="state.form.path" placeholder="路由中的 path 值" clearable></el-input>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
              <el-form-item label="路由参数">
                <el-input v-model="state.form.query" placeholder="请输入路由参数" clearable></el-input>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
              <el-form-item label="菜单图标">
                <IconSelector placeholder="请输入菜单图标" v-model="state.form.icon" type="all"/>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
              <el-form-item label="组件路径" prop="component">
                <el-input v-model="state.form.component" placeholder="组件路径" clearable></el-input>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
              <el-form-item label="权限标识">
                <el-input v-model="state.form.perms" placeholder="如：system:menu" clearable></el-input>
                <div class="form-tip">菜单权限标识，用于特殊权限控制（可选）</div>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
              <el-form-item label="菜单排序">
                <el-input-number v-model="state.form.order_num" controls-position="right" placeholder="请输入排序" class="w100"/>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
              <el-form-item label="是否可见">
                <el-radio-group v-model="state.form.visible">
                  <el-radio :value="1">显示</el-radio>
                  <el-radio :value="0">隐藏</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
              <el-form-item label="菜单状态">
                <el-radio-group v-model="state.form.status">
                  <el-radio :value="1">启用</el-radio>
                  <el-radio :value="0">禁用</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
              <el-form-item label="是否缓存">
                <el-radio-group v-model="state.form.is_cache">
                  <el-radio :value="1">缓存</el-radio>
                  <el-radio :value="0">不缓存</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
              <el-form-item label="是否外链">
                <el-radio-group v-model="state.form.is_frame">
                  <el-radio :value="1">是</el-radio>
                  <el-radio :value="0">否</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
              <el-form-item label="备注">
                <el-input v-model="state.form.remark" type="textarea" placeholder="请输入备注" maxlength="500"></el-input>
              </el-form-item>
            </el-col>
          </template>
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

<script lang="ts" setup name="SaveOrUpdateMenu">
import {onMounted, reactive, ref} from 'vue';
import IconSelector from '/@/components/iconSelector/index.vue';
import {useMenuApi} from "/@/api/v1/system/menu";
import {ElMessage} from "element-plus";

const emit = defineEmits(['getList'])
const props = defineProps({
  allMenuList: {
    type: Array,
  },
  menuList: {
    type: Array,
  }
})

const formRef = ref();

const createMenuForm = () => {
  return {
    id: null,
    parent_id: 0, // 上级菜单
    menu_type: 'C', // 菜单类型  M:目录  C:菜单  F:按钮
    menu_name: '', // 菜单名称
    component_name: '', // 组件名称（路由name）
    component: '', // 组件路径
    order_num: 0, // 菜单排序
    path: '', // 路由路径
    query: '', // 路由参数
    icon: '', // 菜单图标
    perms: '', // 权限标识
    visible: 1, // 是否可见 1:显示 0:隐藏
    status: 1, // 状态 1:启用 0:禁用
    is_frame: 1, // 是否外链 1:是 0:否
    is_cache: 0, // 是否缓存 1:缓存 0:不缓存
    remark: '', // 备注
  }
}

const state = reactive({
  isShowDialog: false,
  editType: '',
  // 参数请参考 `/src/router/route.ts` 中的 `dynamicRoutes` 路由菜单格式
  form: createMenuForm(),
  rules: {
    menu_name: [{required: true, message: '请输入菜单名称', trigger: 'blur'}],
    parent_id: [{required: true, message: '请选择上级菜单', trigger: 'change'}],
    menu_type: [{required: true, message: '请选择菜单类型', trigger: 'change'}],
    component: [
      {
        validator: (rule: any, value: any, callback: any) => {
          // 只有菜单类型(C)需要组件路径
          if (state.form.menu_type === 'C' && !value) {
            callback(new Error('请输入组件路径'));
          } else {
            callback();
          }
        },
        trigger: 'blur'
      }
    ],
    path: [
      {
        validator: (rule: any, value: any, callback: any) => {
          // 目录(M)和菜单(C)需要路由路径
          if ((state.form.menu_type === 'M' || state.form.menu_type === 'C') && !value) {
            callback(new Error('请输入路由路径'));
          } else {
            callback();
          }
        },
        trigger: 'blur'
      }
    ],
    component_name: [
      {
        validator: (rule: any, value: any, callback: any) => {
          // 目录(M)和菜单(C)需要组件名称
          if ((state.form.menu_type === 'M' || state.form.menu_type === 'C') && !value) {
            callback(new Error('请输入组件名称'));
          } else {
            callback();
          }
        },
        trigger: 'blur'
      }
    ],
    perms: [
      {
        validator: (rule: any, value: any, callback: any) => {
          // 按钮类型(F)必须有权限标识
          if (state.form.menu_type === 'F' && !value) {
            callback(new Error('请输入权限标识'));
          } else {
            callback();
          }
        },
        trigger: 'blur'
      }
    ],
  },
  menuData: [], // 上级菜单数据
});
// 创建表单

// 打开弹窗
const openDialog = (editType: string, row: any) => {
  state.editType = editType
  if (row) {
    // 深拷贝数据
    const rowData = JSON.parse(JSON.stringify(row));
    
    // 字段映射：后端 -> 前端
    state.form = {
      id: rowData.id || null,
      parent_id: rowData.parent_id !== undefined ? rowData.parent_id : 0,
      menu_type: rowData.menu_type || 'C',
      menu_name: rowData.menu_name || rowData.title || '',
      component_name: rowData.component_name || rowData.name || '',  // 组件名称（路由name）
      component: rowData.component || '',
      order_num: rowData.order_num !== undefined ? rowData.order_num : (rowData.sort !== undefined ? rowData.sort : 0),
      path: rowData.path || '',
      query: rowData.query || '',
      icon: rowData.icon || '',
      perms: rowData.perms || rowData.permission || '',
      visible: rowData.visible !== undefined ? rowData.visible : 1,
      status: rowData.status !== undefined ? rowData.status : 1,
      is_frame: rowData.is_frame !== undefined ? rowData.is_frame : (rowData.isIframe !== undefined ? rowData.isIframe : 1),
      is_cache: rowData.is_cache !== undefined ? rowData.is_cache : (rowData.isKeepAlive !== undefined ? rowData.isKeepAlive : 0),
      remark: rowData.remark || '',
    };
    
    // 清理无效的perms值
    if (state.form.perms === 0 || state.form.perms === '0' || state.form.perms === 'False') {
      state.form.perms = '';
    }
  } else {
    state.form = createMenuForm()
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
// 新增
const saveOrUpdate = () => {
  formRef.value.validate((valid: boolean) => {
    if (!valid) return;
    
    // 处理空字符串字段，转为null
    const formData = { ...state.form };
    if (formData.remark === '') formData.remark = null;
    if (formData.query === '') formData.query = null;
    if (formData.perms === '') formData.perms = null;
    if (formData.icon === '') formData.icon = null;
    
    useMenuApi().saveOrUpdate(formData)
        .then(() => {
          ElMessage.success('操作成功');
          closeDialog(); // 先关闭弹窗
          // 延迟刷新，确保后端数据已保存
          setTimeout(() => {
            emit('getList')
          }, 100)
        })
        .catch(error => {
          ElMessage.error(error.message || '操作失败');
        });
  });
};
// 页面加载时
onMounted(() => {
  // 初始化完成
});


defineExpose({
  openDialog,
})

</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
  line-height: 1.5;
}
</style>
