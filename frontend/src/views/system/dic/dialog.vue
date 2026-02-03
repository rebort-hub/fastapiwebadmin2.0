<template>
	<div class="system-dic-dialog-container">
		<el-dialog :title="state.dialog.title" v-model="state.dialog.isShowDialog" width="600px">
			<el-form ref="dicDialogFormRef" :model="state.ruleForm" :rules="state.rules" size="default" label-width="90px">
				<el-row :gutter="35">
					<el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
						<el-form-item label="字典名称" prop="dict_name">
							<el-input v-model="state.ruleForm.dict_name" placeholder="请输入字典名称" clearable />
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
						<el-form-item label="字典类型" prop="dict_type">
							<el-input 
								v-model="state.ruleForm.dict_type" 
								placeholder="请输入字典类型（如：sys_user_sex）" 
								clearable
								:disabled="state.dialog.type === 'edit'"
							/>
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
						<el-form-item label="状态">
							<el-switch 
								v-model="state.ruleForm.status" 
								:active-value="1"
								:inactive-value="0"
								inline-prompt 
								active-text="启" 
								inactive-text="禁"
							/>
						</el-form-item>
					</el-col>
					<el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
						<el-form-item label="备注">
							<el-input 
								v-model="state.ruleForm.remark" 
								type="textarea" 
								placeholder="请输入备注" 
								maxlength="500"
								:rows="4"
							/>
						</el-form-item>
					</el-col>
				</el-row>
			</el-form>
			<template #footer>
				<span class="dialog-footer">
					<el-button @click="onCancel">取 消</el-button>
					<el-button type="primary" @click="onSubmit">确 定</el-button>
				</span>
			</template>
		</el-dialog>
	</div>
</template>

<script setup lang="ts" name="systemDicDialog">
import { reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { useDictTypeApi } from '/@/api/v1/system/dict';

// 定义子组件向父组件传值/事件
const emit = defineEmits(['refresh']);

// 定义变量内容
const dicDialogFormRef = ref();
const state = reactive({
	ruleForm: {
		id: null as number | null,
		dict_name: '',
		dict_type: '',
		status: 1,
		remark: '',
	},
	rules: {
		dict_name: [
			{ required: true, message: '请输入字典名称', trigger: 'blur' }
		],
		dict_type: [
			{ required: true, message: '请输入字典类型', trigger: 'blur' },
			{ pattern: /^[a-z_]+$/, message: '字典类型只能包含小写字母和下划线', trigger: 'blur' }
		],
	},
	dialog: {
		isShowDialog: false,
		type: '',
		title: '',
	},
});

// 打开弹窗
const openDialog = (type: string, row?: any) => {
	state.dialog.type = type;
	
	if (type === 'edit' && row) {
		state.ruleForm = {
			id: row.id,
			dict_name: row.dict_name,
			dict_type: row.dict_type,
			status: row.status,
			remark: row.remark || '',
		};
		state.dialog.title = '修改字典类型';
	} else {
		state.ruleForm = {
			id: null,
			dict_name: '',
			dict_type: '',
			status: 1,
			remark: '',
		};
		state.dialog.title = '新增字典类型';
	}
	state.dialog.isShowDialog = true;
};

// 关闭弹窗
const closeDialog = () => {
	state.dialog.isShowDialog = false;
};

// 取消
const onCancel = () => {
	closeDialog();
};

// 提交
const onSubmit = () => {
	dicDialogFormRef.value.validate((valid: boolean) => {
		if (!valid) return;
		
		const formData = { ...state.ruleForm };
		
		useDictTypeApi().saveOrUpdate(formData)
			.then(() => {
				ElMessage.success('操作成功');
				closeDialog();
				emit('refresh');
			})
			.catch(error => {
				ElMessage.error(error.message || '操作失败');
			});
	});
};

// 暴露变量
defineExpose({
	openDialog,
});
</script>
