<template>
  <el-dialog :title="dialogTitle" v-model="visible" width="760px" append-to-body destroy-on-close>
    <el-alert :type="action === 'complete' || action === 'clear' ? 'warning' : 'info'" :closable="false" show-icon class="mb8">
      <template #title>
        <div>你正在对 {{ rows.length }} 个报读课程进行{{ actionLabel }}操作。</div>
        <div v-for="tip in tips" :key="tip">{{ tip }}</div>
      </template>
    </el-alert>

    <el-table :data="rows" border max-height="220" size="small" class="mb8">
      <el-table-column label="学员" prop="studentName" min-width="90" />
      <el-table-column label="报读课程" prop="courseName" min-width="140" show-overflow-tooltip />
      <el-table-column label="剩余" width="90">
        <template #default="scope">{{ scope.row.remainingQuantity }}{{ scope.row.unit || '' }}</template>
      </el-table-column>
      <el-table-column label="有效期至" prop="validEndDate" width="110">
        <template #default="scope">{{ scope.row.validEndDate || '未设置' }}</template>
      </el-table-column>
      <el-table-column label="状态" prop="statusName" width="80" />
    </el-table>

    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
      <template v-if="action === 'transfer'">
        <el-form-item label="转入课程" prop="targetCourseId">
          <el-select v-model="form.targetCourseId" filterable placeholder="请选择转入课程" style="width: 100%" @change="loadClassOptions">
            <el-option v-for="course in courseOptions" :key="course.id" :label="course.courseName" :value="course.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="转入班级">
          <el-select v-model="form.targetClassId" clearable filterable placeholder="可不选，转入后再分班" style="width: 100%">
            <el-option v-for="item in classOptions" :key="item.id" :label="item.className" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程有效期">
          <el-radio-group v-model="form.validityMode">
            <el-radio label="keep">按原课程有效期</el-radio>
            <el-radio label="unified">统一有效期</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="form.validityMode === 'unified'" label="有效期" prop="validEndDate">
          <el-date-picker v-model="form.validStartDate" type="date" value-format="YYYY-MM-DD" placeholder="开始(默认经办日)" style="width: 46%" />
          <span class="sep">至</span>
          <el-date-picker v-model="form.validEndDate" type="date" value-format="YYYY-MM-DD" placeholder="结束日期" style="width: 46%" />
        </el-form-item>
        <el-form-item label="经办日期">
          <el-date-picker v-model="form.enrollDate" type="date" value-format="YYYY-MM-DD" placeholder="默认今天" />
        </el-form-item>
      </template>

      <template v-if="action === 'validity'">
        <el-form-item label="开始日期">
          <el-date-picker v-model="form.validStartDate" type="date" value-format="YYYY-MM-DD" placeholder="不填则不修改" />
        </el-form-item>
        <el-form-item label="结束日期" prop="validEndDate">
          <el-date-picker v-model="form.validEndDate" type="date" value-format="YYYY-MM-DD" placeholder="请选择结束日期" />
        </el-form-item>
      </template>

      <template v-if="action === 'stop'">
        <el-form-item label="停课日期" prop="stopDate">
          <el-date-picker v-model="form.stopDate" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="计划复课日期">
          <el-date-picker v-model="form.plannedResumeDate" type="date" value-format="YYYY-MM-DD" placeholder="仅记录，到期需手动复课" />
        </el-form-item>
      </template>

      <template v-if="action === 'resume'">
        <el-form-item label="复课日期">
          <el-date-picker v-model="form.resumeDate" type="date" value-format="YYYY-MM-DD" placeholder="默认今天" />
        </el-form-item>
      </template>

      <el-form-item :label="reasonRequired ? '备注' : '备注'" prop="reason">
        <el-input
          v-model="form.reason"
          type="textarea"
          :rows="2"
          :maxlength="action === 'stop' ? 30 : 200"
          show-word-limit
          :placeholder="reasonRequired ? '必填' : '选填'"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取 消</el-button>
      <el-button :type="action === 'complete' || action === 'clear' ? 'danger' : 'primary'" :loading="submitting" @click="submit">
        确定{{ actionLabel }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup name="CourseAccountOps">
import { computed, getCurrentInstance, reactive, ref } from 'vue';
import { courseAccountAction } from '@/api/teach/studentAccount';
import { listCourseOptions } from '@/api/assistant/course';
import { listClassOptions } from '@/api/assistant/class';

const emit = defineEmits(['done']);
const { proxy } = getCurrentInstance();

const ACTIONS = {
  transfer: { label: '转课', allowed: ['active'] },
  clear: { label: '课时清零', allowed: ['active', 'stopped'] },
  validity: { label: '修改有效期', allowed: ['active', 'stopped'] },
  stop: { label: '停课', allowed: ['active'] },
  resume: { label: '复课', allowed: ['stopped'] },
  complete: { label: '结课', allowed: ['active', 'stopped'] }
};
const TIPS = {
  transfer: [
    '仅支持转出全部剩余数量；转出后原课程账户变为“已转出”并移出原班级，转入课程生成 0 元转课订单与新课程账户。',
    '金额不做折算；转入账户的请假免扣次数为 0，需要时请手动调整；转出与转入课程相同或收费方式不同不能转课。'
  ],
  clear: ['所选课程账户的剩余数量将全部清零（记入“已清零”），课程账户保持当前状态，操作记录可在学员详情查看。'],
  validity: ['统一修改所选课程账户的有效期；已结课、已转出的账户不能修改。'],
  stop: ['停课后该课程账户不能点名扣课；复课时课程结束日期按停课天数自动顺延。计划复课日期仅做记录，到期需手动复课。'],
  resume: ['复课后课程结束日期按“复课日期 - 停课日期”的天数顺延。'],
  complete: ['结课后剩余数量将全部清零，学员被移出对应班级，不能再点名扣课，此操作不可撤销。']
};

const visible = ref(false);
const submitting = ref(false);
const action = ref('transfer');
const rows = ref([]);
const courseOptions = ref([]);
const classOptions = ref([]);
const formRef = ref();
const form = reactive({});

const actionLabel = computed(() => ACTIONS[action.value]?.label || '');
const dialogTitle = computed(() => `批量${actionLabel.value}`);
const tips = computed(() => TIPS[action.value] || []);
const reasonRequired = computed(() => ['clear', 'stop'].includes(action.value));
const rules = computed(() => ({
  targetCourseId: [{ required: true, message: '请选择转入课程', trigger: 'change' }],
  validEndDate: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
  stopDate: [{ required: true, message: '请选择停课日期', trigger: 'change' }],
  reason: reasonRequired.value ? [{ required: true, message: '请填写备注', trigger: 'blur' }] : []
}));

function today() {
  return proxy.parseTime(new Date(), '{y}-{m}-{d}');
}

async function open(nextAction, selectedRows) {
  const config = ACTIONS[nextAction];
  if (!config) return;
  const list = (selectedRows || []).filter(Boolean);
  if (!list.length) {
    proxy.$modal.msgWarning('请先选择报读课程');
    return;
  }
  const invalid = list.filter(row => !config.allowed.includes(row.status));
  if (invalid.length) {
    proxy.$modal.msgWarning(`${invalid[0].studentName || ''}的${invalid[0].courseName}当前为“${invalid[0].statusName}”，不能${config.label}`);
    return;
  }
  action.value = nextAction;
  rows.value = list;
  Object.keys(form).forEach(key => delete form[key]);
  Object.assign(form, {
    targetCourseId: null,
    targetClassId: null,
    validityMode: 'keep',
    validStartDate: null,
    validEndDate: null,
    enrollDate: null,
    stopDate: today(),
    plannedResumeDate: null,
    resumeDate: null,
    reason: ''
  });
  classOptions.value = [];
  if (nextAction === 'transfer' && !courseOptions.value.length) {
    const res = await listCourseOptions();
    courseOptions.value = res.data || [];
  }
  visible.value = true;
}

async function loadClassOptions(courseId) {
  form.targetClassId = null;
  classOptions.value = [];
  if (!courseId) return;
  const res = await listClassOptions({ course_id: courseId });
  classOptions.value = (res.data || []).filter(item => item.courseId === courseId);
}

function buildPayload() {
  const payload = { accountIds: rows.value.map(row => row.id), reason: form.reason || null };
  if (action.value === 'transfer') {
    Object.assign(payload, {
      targetCourseId: form.targetCourseId,
      targetClassId: form.targetClassId || null,
      validityMode: form.validityMode,
      validStartDate: form.validityMode === 'unified' ? form.validStartDate : null,
      validEndDate: form.validityMode === 'unified' ? form.validEndDate : null,
      enrollDate: form.enrollDate || null
    });
  } else if (action.value === 'validity') {
    Object.assign(payload, { validStartDate: form.validStartDate || null, validEndDate: form.validEndDate });
  } else if (action.value === 'stop') {
    Object.assign(payload, { stopDate: form.stopDate, plannedResumeDate: form.plannedResumeDate || null });
  } else if (action.value === 'resume') {
    payload.resumeDate = form.resumeDate || null;
  }
  return payload;
}

function submit() {
  formRef.value.validate(async valid => {
    if (!valid) return;
    if (action.value === 'transfer' && form.validityMode === 'unified' && !form.validEndDate) {
      proxy.$modal.msgWarning('请选择统一有效期的结束日期');
      return;
    }
    if (['complete', 'clear'].includes(action.value)) {
      await proxy.$modal.confirm(`确定对 ${rows.value.length} 个报读课程${actionLabel.value}？剩余数量将清零且不可撤销。`);
    }
    submitting.value = true;
    try {
      const res = await courseAccountAction(action.value, buildPayload());
      proxy.$modal.msgSuccess(res.msg || `${actionLabel.value}成功`);
      visible.value = false;
      emit('done', action.value);
    } finally {
      submitting.value = false;
    }
  });
}

defineExpose({ open });
</script>

<style scoped>
.sep { margin: 0 6px; color: #909399; }
.mb8 { margin-bottom: 8px; }
</style>
