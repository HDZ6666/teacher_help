<template>
  <el-dialog v-model="visible" :title="`点名：${classInfo.className || ''}`" width="1000px" append-to-body @open="loadData">
    <div v-loading="loading">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="86px">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="上课日期" prop="classDate">
              <el-date-picker v-model="form.classDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="上课时间" required>
              <div class="time-range">
                <el-time-picker v-model="form.startTime" format="HH:mm" value-format="HH:mm" placeholder="开始" />
                <span>-</span>
                <el-time-picker v-model="form.endTime" format="HH:mm" value-format="HH:mm" placeholder="结束" />
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="授课课时">
              <el-input-number v-model="form.lessonHours" :min="0" :max="999" :precision="2" :step="0.5" controls-position="right" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="上课老师">
              <el-input v-model="form.teacherName" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="上课教室">
              <el-input v-model="form.classroom" maxlength="100" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="上课内容">
              <el-input v-model="form.content" maxlength="500" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <div class="toolbar-line">
        <el-button size="small" type="success" @click="setAllStatus(1)">全部到课</el-button>
        <el-button size="small" @click="setAllStatus(4)">全部未到</el-button>
        <span class="muted">共 {{ students.length }} 人，到课{{ stat.present }} 迟到{{ stat.late }} 请假{{ stat.leave }} 未到{{ stat.absent }}，扣课{{ stat.deducted }}</span>
      </div>
      <el-table :data="students" border max-height="420">
        <el-table-column label="姓名" min-width="150">
          <template #default="{ row }">
            <span>{{ row.studentName }}</span>
            <el-tag v-if="row.isTemp === 1" size="small" type="info" class="ml6">{{ row.makeupDetailId ? '补课' : '临时' }}</el-tag>
            <el-tag v-else-if="row.makeupDetailId" size="small" type="info" class="ml6">补课</el-tag>
            <el-tag v-if="row.leaveId" size="small" type="warning" class="ml6">已请假{{ row.leaveIsDeduct === 1 ? '(扣课时)' : '' }}</el-tag>
            <div class="muted">{{ row.phone || '-' }}</div>
          </template>
        </el-table-column>
        <el-table-column label="消费方式" prop="consumeMethod" min-width="180" show-overflow-tooltip />
        <el-table-column label="剩余" width="90" align="center">
          <template #default="{ row }">
            <span v-if="row.remainingQuantity !== null && row.remainingQuantity !== undefined">{{ row.remainingQuantity }}{{ row.remainingType || '' }}</span>
            <span v-else class="muted">未绑定</span>
          </template>
        </el-table-column>
        <el-table-column label="到课状态" width="250" align="center">
          <template #default="{ row }">
            <el-radio-group v-model="row.attendanceStatus" size="small" @change="handleStatusChange(row)">
              <el-radio-button :label="1">到课</el-radio-button>
              <el-radio-button :label="2">迟到</el-radio-button>
              <el-radio-button :label="3">请假</el-radio-button>
              <el-radio-button :label="4">未到</el-radio-button>
            </el-radio-group>
          </template>
        </el-table-column>
        <el-table-column label="扣除额度" width="130" align="center">
          <template #default="{ row }">
            <el-input-number
              v-model="row.deductQuantity"
              :min="0"
              :max="row.remainingQuantity ?? 999"
              :disabled="!canDeduct(row)"
              size="small"
              controls-position="right"
            />
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="140">
          <template #default="{ row }">
            <el-input v-model="row.remark" size="small" maxlength="500" />
          </template>
        </el-table-column>
      </el-table>
    </div>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="warning" :loading="submitting" @click="submit">完成点名</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, getCurrentInstance, reactive, ref } from 'vue'
import { getClassAttendancePrepare, submitClassAttendance } from '@/api/assistant/class'

// 课表课次详情内直接点名：复用班级点名准备/提交接口（后端同一套加锁与扣课规则）
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  classId: { type: [Number, String], default: null },
  eventId: { type: [Number, String], default: null }
})
const emit = defineEmits(['update:modelValue', 'success'])
const { proxy } = getCurrentInstance()

const visible = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value)
})
const loading = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const classInfo = ref({})
const students = ref([])
const form = reactive({
  eventId: null,
  classDate: '',
  startTime: '',
  endTime: '',
  teacherId: null,
  teacherName: '',
  classroom: '',
  lessonHours: 1,
  content: ''
})
const rules = { classDate: [{ required: true, message: '请选择上课日期', trigger: 'change' }] }

const stat = computed(() => students.value.reduce((result, item) => {
  if (item.attendanceStatus === 1) result.present += 1
  if (item.attendanceStatus === 2) result.late += 1
  if (item.attendanceStatus === 3) result.leave += 1
  if (item.attendanceStatus === 4) result.absent += 1
  result.deducted += Number(item.deductQuantity || 0)
  return result
}, { present: 0, late: 0, leave: 0, absent: 0, deducted: 0 }))

async function loadData() {
  students.value = []
  loading.value = true
  try {
    const response = await getClassAttendancePrepare(props.classId, { eventId: props.eventId })
    const data = response.data || {}
    classInfo.value = data.classInfo || {}
    Object.assign(form, data.form || {})
    students.value = data.students || []
  } catch (e) {
    visible.value = false
  } finally {
    loading.value = false
  }
}

function canDeduct(row) {
  if (!row.courseAccountId) return false
  if (row.attendanceStatus === 1 || row.attendanceStatus === 2) return true
  return row.attendanceStatus === 3 && row.leaveIsDeduct === 1
}

function handleStatusChange(row) {
  if (canDeduct(row)) {
    row.deductQuantity = Number(row.remainingQuantity || 0) > 0 ? (row.deductQuantity || 1) : 0
    if (row.remainingQuantity !== null && row.remainingQuantity !== undefined && row.deductQuantity > row.remainingQuantity) {
      row.deductQuantity = row.remainingQuantity
    }
  } else {
    row.deductQuantity = 0
  }
}

function setAllStatus(status) {
  students.value.forEach(item => {
    item.attendanceStatus = status
    handleStatusChange(item)
  })
}

function submit() {
  formRef.value.validate(async valid => {
    if (!valid) return
    if (!form.startTime || !form.endTime || form.endTime <= form.startTime) {
      proxy.$modal.msgWarning('请正确选择上课时间')
      return
    }
    if (!students.value.length) {
      proxy.$modal.msgWarning('本课次没有可点名学员')
      return
    }
    submitting.value = true
    try {
      await submitClassAttendance(props.classId, {
        eventId: props.eventId,
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
      })
      proxy.$modal.msgSuccess('点名完成')
      visible.value = false
      emit('success')
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style scoped>
.time-range {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
}

.toolbar-line {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.muted {
  color: #909399;
  font-size: 12px;
}

.ml6 {
  margin-left: 6px;
}
</style>
