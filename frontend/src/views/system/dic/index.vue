<template>
	<div class="system-dic-container layout-padding">
		<el-card shadow="hover" class="layout-padding-auto">
			<div class="system-user-search mb15">
				<el-input 
					v-model="state.searchForm.dict_name"
					placeholder="请输入字典名称" 
					style="max-width: 180px"
					clearable
					@keyup.enter="onSearch"
				/>
				<el-input 
					v-model="state.searchForm.dict_type"
					placeholder="请输入字典类型" 
					style="max-width: 180px"
					class="ml10"
					clearable
					@keyup.enter="onSearch"
				/>
				<el-select 
					v-model="state.searchForm.status"
					placeholder="字典状态" 
					clearable
					style="max-width: 120px"
					class="ml10"
				>
					<el-option label="启用" :value="1" />
					<el-option label="禁用" :value="0" />
				</el-select>
				<el-button v-auth="'system:dict:type:list'" type="primary" class="ml10" @click="onSearch">
					<el-icon>
						<ele-Search />
					</el-icon>
					查询
				</el-button>
				<el-button class="ml10" @click="onReset">
					<el-icon>
						<ele-RefreshRight />
					</el-icon>
					重置
				</el-button>
				<el-button 
					v-auth="'system:dict:type:add'"
					type="success" 
					class="ml10" 
					@click="onOpenAddDic('add')"
				>
					<el-icon>
						<ele-FolderAdd />
					</el-icon>
					新增字典
				</el-button>
			</div>
			<el-table :data="state.tableData.data" v-loading="state.tableData.loading" style="width: 100%" stripe>
				<el-table-column type="index" label="序号" width="60" />
				<el-table-column prop="dict_name" label="字典名称" show-overflow-tooltip width="150" />
				<el-table-column prop="dict_type" label="字典类型" show-overflow-tooltip width="150" />
				<el-table-column prop="status" label="状态" show-overflow-tooltip width="80" align="center">
					<template #default="scope">
						<el-tag type="success" v-if="scope.row.status === 1">启用</el-tag>
						<el-tag type="info" v-else>禁用</el-tag>
					</template>
				</el-table-column>
				<el-table-column prop="remark" label="备注" show-overflow-tooltip />
				<el-table-column prop="created_at" label="创建时间" show-overflow-tooltip width="160" align="center">
					<template #default="scope">
						{{ formatDateTime(scope.row.created_at) }}
					</template>
				</el-table-column>
				<el-table-column label="操作" width="200" fixed="right" align="center">
					<template #default="scope">
						<el-button 
							v-auth="'system:dict:type:edit'"
							size="small" 
							type="primary"
							@click="onOpenEditDic('edit', scope.row)"
						>
							修改
						</el-button>
						<el-button 
							v-auth="'system:dict:data:query'"
							size="small" 
							type="primary"
							@click="onOpenDictData(scope.row)"
						>
							数据
						</el-button>
						<el-button 
							v-auth="'system:dict:type:delete'"
							size="small" 
							type="danger"
							@click="onRowDel(scope.row)"
						>
							删除
						</el-button>
					</template>
				</el-table-column>
			</el-table>
			<el-pagination
				@size-change="onHandleSizeChange"
				@current-change="onHandleCurrentChange"
				class="mt15"
				:pager-count="5"
				:page-sizes="[10, 20, 30, 50]"
				v-model:current-page="state.tableData.param.page"
				background
				v-model:page-size="state.tableData.param.page_size"
				layout="total, sizes, prev, pager, next, jumper"
				:total="state.tableData.total"
			/>
		</el-card>
		<DicDialog ref="dicDialogRef" @refresh="getTableData()" />
		<DictDataDialog ref="dictDataDialogRef" />
	</div>
</template>

<script setup lang="ts" name="systemDic">
import { defineAsyncComponent, reactive, onMounted, ref } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import { useDictTypeApi } from '/@/api/v1/system/dict';
import { formatDateTime } from '/@/utils/formatTime';

// 引入组件
const DicDialog = defineAsyncComponent(() => import('/@/views/system/dic/dialog.vue'));
const DictDataDialog = defineAsyncComponent(() => import('/@/views/system/dic/dataDialog.vue'));

// 定义变量内容
const dicDialogRef = ref();
const dictDataDialogRef = ref();
const state = reactive({
	searchForm: {
		dict_name: '',
		dict_type: '',
		status: undefined as number | undefined,
	},
	tableData: {
		data: [],
		total: 0,
		loading: false,
		param: {
			page: 1,
			page_size: 10,
		},
	},
});

// 初始化表格数据
const getTableData = () => {
	state.tableData.loading = true;
	const params = {
		page: state.tableData.param.page,
		page_size: state.tableData.param.page_size,
		dict_name: state.searchForm.dict_name || undefined,
		dict_type: state.searchForm.dict_type || undefined,
		status: state.searchForm.status,
	};
	
	useDictTypeApi().getList(params)
		.then(res => {
			state.tableData.data = res.data?.items || [];
			state.tableData.total = res.data?.total || 0;
		})
		.catch(error => {
			ElMessage.error(error.message || '获取字典列表失败');
		})
		.finally(() => {
			state.tableData.loading = false;
		});
};

// 搜索
const onSearch = () => {
	state.tableData.param.page = 1;
	getTableData();
};

// 重置
const onReset = () => {
	state.searchForm.dict_name = '';
	state.searchForm.dict_type = '';
	state.searchForm.status = undefined;
	state.tableData.param.page = 1;
	getTableData();
};

// 打开新增字典弹窗
const onOpenAddDic = (type: string) => {
	dicDialogRef.value.openDialog(type);
};

// 打开修改字典弹窗
const onOpenEditDic = (type: string, row: any) => {
	dicDialogRef.value.openDialog(type, row);
};

// 打开字典数据管理
const onOpenDictData = (row: any) => {
	dictDataDialogRef.value.openDialog(row);
};

// 删除字典
const onRowDel = (row: any) => {
	ElMessageBox.confirm(`此操作将永久删除字典"${row.dict_name}"，是否继续?`, '提示', {
		confirmButtonText: '确认',
		cancelButtonText: '取消',
		type: 'warning',
	})
		.then(() => {
			useDictTypeApi().delete(row.id)
				.then(() => {
					ElMessage.success('删除成功');
					getTableData();
				})
				.catch(error => {
					ElMessage.error(error.message || '删除失败');
				});
		})
		.catch(() => {});
};

// 分页改变
const onHandleSizeChange = (val: number) => {
	state.tableData.param.page_size = val;
	getTableData();
};

// 分页改变
const onHandleCurrentChange = (val: number) => {
	state.tableData.param.page = val;
	getTableData();
};

// 页面加载时
onMounted(() => {
	getTableData();
});
</script>
