<template>
  <div>
    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['teach:student:follow']">填写跟进记录</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-select v-model="query.followType" placeholder="跟进方式" clearable style="width: 140px" @change="reload">
          <el-option v-for="(label, key) in FOLLOW_TYPES" :key="key" :label="label" :value="key" />
        </el-select>
      </el-col>
    </el-row>

    <el-table v-loading="loading" :data="list" border>
      <el-table-column label="跟进时间" prop="followTime" width="170" />
      <el-table-column label="跟进方式" prop="followTypeName" width="90" />
      <el-table-column label="跟进阶段" prop="followStage" width="120">
        <template #default="scope">{{ scope.row.followStage || '-' }}</template>
      </el-table-column>
      <el-table-column label="跟进内容" prop="content" min-width="260" show-overflow-tooltip />
      <el-table-column label="下次跟进" prop="nextFollowDate" width="110">
        <template #default="scope">{{ scope.row.nextFollowDate || '-' }}</template>
      </el-table-column>
      <el-table-column label="跟进人" prop="followUserName" width="100" />
      <el-table-column label="操作" width="130" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="handleEdit(scope.row)" v-hasPermi="['teach:student:follow']">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(scope.row)" v-hasPermi="['teach:student:follow']">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total > 0" :total="total" v-model:page="query.pageNum" v-model:limit="query.pageSize" @pagination="getList" />

    <el-dialog :title="form.id ? '编辑跟进记录' : '填写跟进记录'" v-model="open" width="600px" append-to-body destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="跟进方式" prop="followType">
          <el-radio-group v-model="form.followType">
            <el-radio v-for="(label, key) in FOLLOW_TYPES" :key="key" :label="key">{{ label }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="跟进阶段" prop="followStage">
          <el-input v-model="form.followStage" maxlength="50" placeholder="选填，如：意向沟通、续费提醒" />
        </el-form-item>
        <el-form-item label="跟进内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="4" maxlength="2000" show-word-limit />
        </el-form-item>
        <el-form-item label="跟进时间" prop="followTime">
          <el-date-picker v-model="form.followTime" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" placeholder="默认当前时间" />
        </el-form-item>
        <el-form-item label="下次跟进" prop="nextFollowDate">
          <el-date-picker v-model="form.nextFollowDate" type="date" value-format="YYYY-MM-DD" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="open = false">取 消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">保 存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="StudentFollowPanel">
import { getCurrentInstance, onMounted, reactive, ref } from 'vue';
import { addStudentFollow, delStudentFollow, listStudentFollow, updateStudentFollow } from '@/api/teach/studentAccount';

const props = defineProps({ studentId: { type: Number, required: true } });
const { proxy } = getCurrentInstance();
const FOLLOW_TYPES = { phone: '电话', wechat: '微信', visit: '面谈', other: '其他' };

const loading = ref(false);
const list = ref([]);
const total = ref(0);
const query = reactive({ pageNum: 1, pageSize: 10, followType: null });
const open = ref(false);
const saving = ref(false);
const formRef = ref();
const form = ref({});
const rules = {
  followType: [{ required: true, message: '请选择跟进方式', trigger: 'change' }],
  content: [{ required: true, message: '请填写跟进内容', trigger: 'blur' }]
};

async function getList() {
  loading.value = true;
  try {
    const res = await listStudentFollow({ ...query, studentId: props.studentId });
    list.value = res.rows || [];
    total.value = res.total || 0;
  } finally {
    loading.value = false;
  }
}

function reload() {
  query.pageNum = 1;
  getList();
}

function handleAdd() {
  form.value = { studentId: props.studentId, followType: 'phone', followStage: '', content: '', followTime: null, nextFollowDate: null };
  open.value = true;
}

function handleEdit(row) {
  form.value = {
    id: row.id,
    studentId: props.studentId,
    followType: row.followType,
    followStage: row.followStage,
    content: row.content,
    followTime: row.followTime,
    nextFollowDate: row.nextFollowDate
  };
  open.value = true;
}

function submit() {
  formRef.value.validate(async valid => {
    if (!valid) return;
    saving.value = true;
    try {
      const payload = { ...form.value, followTime: form.value.followTime || null, nextFollowDate: form.value.nextFollowDate || null };
      const res = payload.id ? await updateStudentFollow(payload) : await addStudentFollow(payload);
      proxy.$modal.msgSuccess(res.msg || '保存成功');
      open.value = false;
      getList();
    } finally {
      saving.value = false;
    }
  });
}

async function handleDelete(row) {
  await proxy.$modal.confirm('确定删除这条跟进记录？');
  const res = await delStudentFollow(row.id);
  proxy.$modal.msgSuccess(res.msg || '删除成功');
  getList();
}

onMounted(getList);
defineExpose({ getList });
</script>
