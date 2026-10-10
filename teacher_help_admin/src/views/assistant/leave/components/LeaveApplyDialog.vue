<template>
  <el-dialog :model-value="modelValue" title="给学员请假" width="560px" append-to-body @update:model-value="val => emit('update:modelValue', val)" @open="init">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="学员" prop="studentId">
        <student-select v-model="form.studentId" :initial-label="preset.studentName || ''" :disabled="!!preset.studentId" />
      </el-form-item>
      <el-form-item label="班级">
        <el-select v-model="form.classId" clearable filterable placeholder="选择班级后可指定课次" style="width: 100%" :disabled="!!preset.classId" @change="handleClassChange">
          <el-option v-for="item in classOptions" :key="item.id" :label="item.className" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="请假日期" prop="leaveDate">
        <el-date-picker v-model="form.leaveDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" @change="loadEvents" />
      </el-form-item>
      <el-form-item label="请假课次">
        <el-select v-model="form.eventId" clearable placeholder="不选则按日期请假" style="width: 100%" :disabled="!form.classId" :loading="eventLoading" @change="handleEventChange">
          <el-option v-for="event in events" :key="event.id" :label="formatEvent(event)" :value="event.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="请假类型">
        <el-radio-group v-model="form.leaveType">
          <el-radio :value="1">事假</el-radio>
          <el-radio :value="2">病假</el-radio>
          <el-radio :value="3">其他</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="是否扣课">
        <el-radio-group v-model="form.isDeduct">
          <el-radio :value="0">不扣课时</el-radio>
          <el-radio :value="1">扣课时</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="请假事由" prop="leaveReason">
        <el-input v-model="form.leaveReason" type="textarea" :rows="3" maxlength="500" show-word-limit />
      </el-form-item>
      <el-alert type="info" :closable="false" show-icon title="提交后为“待审批”，审批通过后同步到点名：课次已点名的只把“未到”更正为“请假”，不追加扣课" />
    </el-form>
    <template #footer>
      <el-button @click="emit('update:modelValue', false)">取 消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">提 交</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { getCurrentInstance, ref } from 'vue'
import { addLeaveApplication } from '@/api/assistant/classRecord'
import { listClassOptions } from '@/api/assistant/class'
import { listScheduleEvent } from '@/api/teach/schedule'
import StudentSelect from '@/components/StudentSelect'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  // 预置：{ studentId, studentName, classId, eventId, leaveDate }
  preset: { type: Object, default: () => ({}) }
})
const emit = defineEmits(['update:modelValue', 'success'])
const { proxy } = getCurrentInstance()

const form = ref({})
const classOptions = ref([])
const events = ref([])
const eventLoading = ref(false)
const submitting = ref(false)
const rules = {
  studentId: [{ required: true, message: '请选择学员', trigger: 'change' }],
  leaveDate: [{ required: true, message: '请选择请假日期', trigger: 'change' }],
  leaveReason: [{ required: true, message: '请输入请假事由', trigger: 'blur' }]
}

async function init() {
  form.value = {
    studentId: props.preset.studentId,
    classId: props.preset.classId,
    eventId: props.preset.eventId,
    leaveDate: props.preset.leaveDate,
    leaveType: 1,
    isDeduct: 0,
    leaveReason: ''
  }
  events.value = []
  proxy.resetForm('formRef')
  try {
    const res = await listClassOptions({})
    classOptions.value = res.data || []
  } catch (error) {
    classOptions.value = []
  }
  if (form.value.classId && form.value.leaveDate) loadEvents()
}

function handleClassChange() {
  form.value.eventId = undefined
  loadEvents()
}

async function loadEvents() {
  events.value = []
  if (!form.value.classId || !form.value.leaveDate) return
  eventLoading.value = true
  try {
    const res = await listScheduleEvent({ pageNum: 1, pageSize: 100, classId: form.value.classId, eventDate: form.value.leaveDate })
    events.value = (res.rows || []).filter(item => String(item.status) !== '3')
    if (form.value.eventId && !events.value.some(item => item.id === form.value.eventId)) form.value.eventId = undefined
  } finally {
    eventLoading.value = false
  }
}

function handleEventChange(eventId) {
  const event = events.value.find(item => item.id === eventId)
  if (event?.eventDate) form.value.leaveDate = event.eventDate
}

function clock(value) {
  return value ? String(value).replace('T', ' ').slice(11, 16) : ''
}

function formatEvent(event) {
  return `${clock(event.startTime)}-${clock(event.endTime)} ${event.courseName || ''} ${event.teacherName || ''}`.trim()
}

function submit() {
  proxy.$refs.formRef.validate(async valid => {
    if (!valid) return
    submitting.value = true
    try {
      await addLeaveApplication({ ...form.value })
      proxy.$modal.msgSuccess('请假申请已提交，待审批')
      emit('update:modelValue', false)
      emit('success')
    } finally {
      submitting.value = false
    }
  })
}
</script>
