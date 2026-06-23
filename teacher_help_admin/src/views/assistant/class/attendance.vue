<template>
  <div class="app-container class-attendance">
    <div class="page-header">
      <el-button icon="ArrowLeft" @click="goBack">返回</el-button>
      <span class="page-title">{{ classInfo.className || '班级点名' }}</span>
    </div>

    <el-card shadow="never" class="mb16">
      <el-form :model="form" ref="formRef" :rules="rules" label-width="96px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="上课日期" prop="classDate">
              <el-date-picker
                v-model="form.classDate"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="请选择日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="上课时间" required>
              <div class="time-range">
                <el-time-picker
                  v-model="form.startTime"
                  format="HH:mm"
                  value-format="HH:mm"
                  placeholder="开始"
                />
                <span>-</span>
                <el-time-picker
                  v-model="form.endTime"
                  format="HH:mm"
                  value-format="HH:mm"
                  placeholder="结束"
                />
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="授课课程">
              <el-input v-model="form.courseName" disabled />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="上课老师">
              <el-input v-model="form.teacherName" disabled placeholder="待分配" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="授课课时">
              <el-input-number v-model="form.lessonHours" :min="0" :max="999" :precision="2" :step="0.5" controls-position="right" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="上课教室">
              <el-input v-model="form.classroom" maxlength="100" placeholder="请输入教室" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="上课内容">
          <el-input v-model="form.content" maxlength="500" placeholder="请输入上课内容" />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <div class="toolbar-line">
        <el-button size="small" type="success" @click="setAllStatus(1)">全部到课</el-button>
        <el-button size="small" @click="setAllStatus(4)">全部未到</el-button>
        <el-input
          v-model="keyword"
          placeholder="搜索学员姓名/手机号"
          clearable
          style="width: 260px; margin-left: auto"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <el-table v-loading="loading" :data="filteredStudents" border>
        <el-table-column label="姓名" min-width="150">
          <template #default="{ row }">
            <div class="student-cell">
              <span>{{ row.studentName }}</span>
              <span class="muted">{{ row.phone || '-' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="消费方式" prop="consumeMethod" min-width="220" show-overflow-tooltip />
        <el-table-column label="剩余额度" width="120" align="center">
          <template #default="{ row }">
            <span v-if="row.remainingQuantity !== null && row.remainingQuantity !== undefined">
              {{ row.remainingQuantity }}{{ row.remainingType || '' }}
            </span>
            <span v-else class="muted">未绑定</span>
          </template>
        </el-table-column>
        <el-table-column label="到课状态" width="260" align="center">
          <template #default="{ row }">
            <el-radio-group v-model="row.attendanceStatus" size="small" @change="handleStatusChange(row)">
              <el-radio-button :label="1">到课</el-radio-button>
              <el-radio-button :label="2">迟到</el-radio-button>
              <el-radio-button :label="3">请假</el-radio-button>
              <el-radio-button :label="4">未到</el-radio-button>
            </el-radio-group>
          </template>
        </el-table-column>
        <el-table-column label="扣除额度" width="150" align="center">
          <template #default="{ row }">
            <el-input-number
              v-model="row.deductQuantity"
              :min="0"
              :max="row.remainingQuantity ?? 999"
              :disabled="row.attendanceStatus === 3 || row.attendanceStatus === 4 || !row.courseAccountId"
              size="small"
              controls-position="right"
            />
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="180">
          <template #default="{ row }">
            <el-input v-model="row.remark" maxlength="500" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <div class="footer-bar">
      <span>到课{{ stat.present }}人</span>
      <span>迟到{{ stat.late }}人</span>
      <span>请假{{ stat.leave }}人</span>
      <span>未到{{ stat.absent }}人</span>
      <span>扣课{{ stat.deducted }}课时</span>
      <el-button @click="goBack">取消</el-button>
      <el-button type="warning" :loading="submitLoading" @click="submitAttendance">完成点名</el-button>
    </div>
  </div>
</template>

<script setup name="ClassAttendance">
import { computed, getCurrentInstance, onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Search } from '@element-plus/icons-vue';
import { getClassAttendancePrepare, submitClassAttendance } from '@/api/assistant/class';

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const classId = computed(() => Number(route.params.id));
const eventId = computed(() => route.query.eventId ? Number(route.query.eventId) : null);

const loading = ref(false);
const submitLoading = ref(false);
const keyword = ref('');
const classInfo = ref({});
const students = ref([]);
const formRef = ref(null);

const form = reactive({
  eventId: null,
  classDate: '',
  startTime: '',
  endTime: '',
  teacherId: null,
  teacherName: '',
  courseName: '',
  classroom: '',
  lessonHours: 1,
  content: ''
});

const rules = {
  classDate: [{ required: true, message: '请选择上课日期', trigger: 'change' }]
};

const filteredStudents = computed(() => {
  const value = keyword.value.trim().toLowerCase();
  if (!value) {
    return students.value;
  }
  return students.value.filter(item => {
    return (item.studentName || '').toLowerCase().includes(value) || (item.phone || '').includes(value);
  });
});

const stat = computed(() => {
  return students.value.reduce((result, item) => {
    if (item.attendanceStatus === 1) result.present += 1;
    if (item.attendanceStatus === 2) result.late += 1;
    if (item.attendanceStatus === 3) result.leave += 1;
    if (item.attendanceStatus === 4) result.absent += 1;
    result.deducted += Number(item.deductQuantity || 0);
    return result;
  }, { present: 0, late: 0, leave: 0, absent: 0, deducted: 0 });
});

async function loadData() {
  loading.value = true;
  try {
    const response = await getClassAttendancePrepare(
      classId.value,
      eventId.value ? { eventId: eventId.value } : undefined
    );
    const data = response.data || {};
    classInfo.value = data.classInfo || {};
    Object.assign(form, data.form || {});
    students.value = data.students || [];
  } finally {
    loading.value = false;
  }
}

function handleStatusChange(row) {
  if (row.attendanceStatus === 1 || row.attendanceStatus === 2) {
    row.deductQuantity = row.courseAccountId && Number(row.remainingQuantity || 0) > 0 ? (row.deductQuantity || 1) : 0;
    if (row.remainingQuantity !== null && row.remainingQuantity !== undefined && row.deductQuantity > row.remainingQuantity) {
      row.deductQuantity = row.remainingQuantity;
    }
  } else {
    row.deductQuantity = 0;
  }
}

function setAllStatus(status) {
  students.value.forEach(item => {
    item.attendanceStatus = status;
    handleStatusChange(item);
  });
}

function submitAttendance() {
  formRef.value.validate(async valid => {
    if (!valid) {
      return;
    }
    if (!form.startTime || !form.endTime) {
      proxy.$modal.msgWarning('请选择上课时间');
      return;
    }
    if (form.endTime <= form.startTime) {
      proxy.$modal.msgWarning('结束时间必须晚于开始时间');
      return;
    }
    if (!students.value.length) {
      proxy.$modal.msgWarning('当前班级没有可点名学员');
      return;
    }
    submitLoading.value = true;
    try {
      const payload = {
        eventId: form.eventId,
        classDate: form.classDate,
        startTime: form.startTime,
        endTime: form.endTime,
        teacherId: form.teacherId,
        classroom: form.classroom,
        lessonHours: form.lessonHours,
        content: form.content,
        details: students.value.map(item => ({
          studentId: item.studentId,
          status: item.attendanceStatus,
          deductQuantity: item.deductQuantity || 0,
          remark: item.remark
        }))
      };
      await submitClassAttendance(classId.value, payload);
      proxy.$modal.msgSuccess('点名完成');
      router.push({ path: `/assistant/class/detail/${classId.value}`, query: { tab: 'attendance' } });
    } finally {
      submitLoading.value = false;
    }
  });
}

function goBack() {
  router.push(`/assistant/class/detail/${classId.value}`);
}

onMounted(() => {
  loadData();
});
</script>

<style scoped lang="scss">
.class-attendance {
  padding-bottom: 76px;

  .page-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;

    .page-title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }
  }

  .mb16 {
    margin-bottom: 16px;
  }

  .time-range {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;

    .el-date-editor {
      flex: 1;
    }
  }

  .toolbar-line {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
  }

  .student-cell {
    display: flex;
    flex-direction: column;
    line-height: 20px;
  }

  .muted {
    color: #909399;
  }

  .footer-bar {
    position: fixed;
    right: 20px;
    bottom: 20px;
    left: 220px;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 16px;
    padding: 12px 16px;
    background: #fff;
    border: 1px solid #ebeef5;
    box-shadow: 0 2px 12px 0 rgb(0 0 0 / 10%);
  }
}
</style>
