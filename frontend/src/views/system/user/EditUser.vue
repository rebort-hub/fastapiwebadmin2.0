<template>
  <div class="system-edit-user-container">
    <el-dialog
        draggable
        :title="state.editType === 'save'? `新增` : `修改`"
        v-model="state.isShowDialog" width="769px">
      <el-form :model="state.form" :rules="state.rules" ref="userFormRef" size="default" label-width="90px">
        <el-row :gutter="35">

          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
            <el-form-item label="账户名称" prop="username">
              <el-input :disabled="state.editType==='update'" v-model="state.form.username" placeholder="请输入账户名称"
                        clearable></el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
            <el-form-item label="用户昵称" prop="nickname">
              <el-input v-model="state.form.nickname" placeholder="请输入用户昵称" clearable></el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
            <el-form-item label="密码" :prop="state.editType === 'save' ? 'password' : ''">
              <el-input 
                v-model="state.form.password" 
                type="password"
                :placeholder="state.editType === 'save' ? '请输入密码（默认123456）' : '留空则不修改密码'" 
                clearable
                show-password
              ></el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
            <el-form-item label="关联角色" prop="role_ids">
              <el-select v-model="state.form.role_ids" multiple placeholder="请选择" clearable class="w100">
                <el-option
                    v-for="item in roleList"
                    :key="item.id"
                    :label="item.name || item.role_name"
                    :value="item.id"
                ></el-option>
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
            <el-form-item label="所属部门">
              <el-tree-select
                v-model="state.form.dept_id"
                :data="state.deptTreeData"
                :props="{ label: 'dept_name', value: 'id' }"
                placeholder="请选择所属部门"
                clearable
                check-strictly
                :render-after-expand="false"
                class="w100"
              />
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="state.form.email" placeholder="请输入" clearable></el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
            <el-form-item label="用户状态">
              <el-switch v-model="state.form.status"
                         :active-value="1"
                         :inactive-value="0"
                         inline-prompt
                         active-text="启"
                         inactive-text="禁"></el-switch>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
            <el-form-item label="用户类型">
              <el-select v-model="state.form.user_type" placeholder="请选择" clearable class="w100">
                <el-option label="超级管理员" :value="10"></el-option>
                <el-option label="普通用户" :value="20"></el-option>
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="用户备注">
              <el-input v-model="state.form.remark" type="textarea" placeholder="请输入用户描述"
                        maxlength="150"></el-input>
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

<script lang="ts" setup name="SaveOrUpdateUser">
import {reactive, ref, onMounted} from 'vue';
import {useUserApi} from "/@/api/v1/system/user";
import {useDeptApi} from "/@/api/v1/system/dept";
import {ElMessage} from "element-plus";

const emit = defineEmits(["getList"])

const props = defineProps({
  roleList: {
    type: Array,
    default: () => []
  }
})

const createForm = () => {
  return {
    id: null,
    username: '',
    nickname: '',
    password: '',
    role_ids: [],  // 改为 role_ids
    email: '',
    status: 1,
    user_type: 20,
    remark: '',  // 改为 remark
    updated_by: null,
    dept_id: null,
  }
}

const userFormRef = ref()
const state = reactive({
  isShowDialog: false,
  editType: 'save',
  form: createForm(),
  deptTreeData: [] as any[],
  rules: {
    username: [{required: true, message: '请输入用户名称', trigger: 'blur'},],
    role_ids: [{required: true, message: '请选择角色', trigger: 'blur'},],
    nickname: [{required: true, message: '请输入用户昵称', trigger: 'blur'},],
    password: [
      {required: true, message: '请输入密码', trigger: 'blur'},
      {min: 6, max: 20, message: '密码长度为6-20个字符', trigger: 'blur'}
    ],
  }
});

// 新增修改窗口初始化
const openDialog = (editType: string, row: any) => {
  state.editType = editType
  getDeptData()
  if (row) {
    state.form = JSON.parse(JSON.stringify(row));
    // 编辑时清空密码字段，避免显示旧密码
    state.form.password = '';
    // 确保使用新字段名
    if (row.roles && !row.role_ids) {
      state.form.role_ids = row.roles;
    }
    if (row.remarks && !row.remark) {
      state.form.remark = row.remarks;
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
  userFormRef.value.validate((valid: any) => {
    if (valid) {
      // 处理空字符串字段，转为null
      const formData = { ...state.form };
      if (formData.email === '') formData.email = null;
      if (formData.phone === '') formData.phone = null;
      if (formData.remark === '') formData.remark = null;
      if (formData.post === '') formData.post = null;
      
      // 编辑时，如果密码为空，删除password字段（不修改密码）
      if (state.editType === 'update' && !formData.password) {
        delete formData.password;
      }
      
      useUserApi().saveOrUpdate(formData)
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
};

// 获取部门数据
const getDeptData = () => {
  useDeptApi().getList()
    .then(res => {
      state.deptTreeData = res.data || [];
    })
    .catch((error) => {
      ElMessage.error(error.message || '获取部门数据失败');
    });
}

defineExpose({
  openDialog,

})

</script>
