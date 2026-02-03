<template>
  <div class="system-edit-permission-container">
    <el-dialog v-model="state.isShowDialog" width="600px" :title="state.title" draggable>
      <el-form ref="formRef" :model="state.ruleForm" :rules="state.rules" label-width="100px">
        <el-form-item label="权限编码" prop="permission_code">
          <el-input v-model="state.ruleForm.permission_code" placeholder="如: user:add" clearable></el-input>
          <div class="form-tip">格式：资源:操作，如 user:add, role:edit</div>
        </el-form-item>

        <el-form-item label="权限名称" prop="permission_name">
          <el-input v-model="state.ruleForm.permission_name" placeholder="如: 新增用户" clearable></el-input>
        </el-form-item>

        <el-form-item label="权限类型" prop="permission_type">
          <el-select v-model="state.ruleForm.permission_type" placeholder="请选择权限类型" style="width: 100%">
            <el-option label="菜单权限" :value="1"></el-option>
            <el-option label="按钮权限" :value="2"></el-option>
            <el-option label="数据权限" :value="3"></el-option>
            <el-option label="API权限" :value="4"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="资源类型" prop="resource_type">
          <el-input v-model="state.ruleForm.resource_type" placeholder="如: user, role, menu" clearable></el-input>
          <div class="form-tip">资源类型，如：user, role, menu, project</div>
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="state.ruleForm.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="state.ruleForm.sort" :min="0" :max="9999" controls-position="right" style="width: 100%"></el-input-number>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input v-model="state.ruleForm.description" type="textarea" :rows="3" placeholder="请输入权限描述"></el-input>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="onCancel">取消</el-button>
          <el-button type="primary" @click="onSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup name="SystemEditPermission">
import {reactive, ref} from 'vue';
import {ElMessage} from 'element-plus';
import {usePermissionApi} from '/@/api/v1/system/permission';

const formRef = ref();
const emit = defineEmits(['getList']);

const state = reactive({
  isShowDialog: false,
  title: '',
  editType: 'add',
  ruleForm: {
    id: null,
    permission_code: '',
    permission_name: '',
    permission_type: 2,
    resource_type: '',
    status: 1,
    sort: 0,
    description: '',
  },
  rules: {
    permission_code: [
      {required: true, message: '请输入权限编码', trigger: 'blur'},
      {pattern: /^[a-z]+:[a-z]+$/i, message: '格式错误，应为：资源:操作', trigger: 'blur'}
    ],
    permission_name: [
      {required: true, message: '请输入权限名称', trigger: 'blur'}
    ],
    permission_type: [
      {required: true, message: '请选择权限类型', trigger: 'change'}
    ],
  },
});

// 打开弹窗
const openDialog = (editType: string, row: any) => {
  state.editType = editType;
  state.title = editType === 'add' ? '新增权限' : '编辑权限';

  if (editType === 'edit' && row) {
    state.ruleForm = {
      id: row.id,
      permission_code: row.permission_code,
      permission_name: row.permission_name,
      permission_type: row.permission_type,
      resource_type: row.resource_type || '',
      status: row.status,
      sort: row.sort || 0,
      description: row.description || '',
    };
  } else {
    resetForm();
  }

  state.isShowDialog = true;
};

// 重置表单
const resetForm = () => {
  state.ruleForm = {
    id: null,
    permission_code: '',
    permission_name: '',
    permission_type: 2,
    resource_type: '',
    status: 1,
    sort: 0,
    description: '',
  };
  formRef.value?.clearValidate();
};

// 取消
const onCancel = () => {
  state.isShowDialog = false;
  resetForm();
};

// 提交
const onSubmit = () => {
  formRef.value.validate(async (valid: boolean) => {
    if (!valid) return;

    try {
      await usePermissionApi().saveOrUpdate(state.ruleForm);
      ElMessage.success(state.editType === 'add' ? '新增成功' : '编辑成功');
      state.isShowDialog = false;
      emit('getList');
      resetForm();
    } catch (error: any) {
      console.error('保存失败:', error);
      ElMessage.error(error.message || '保存失败');
    }
  });
};

// 暴露方法
defineExpose({
  openDialog,
});
</script>

<style scoped lang="scss">
.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}
</style>
