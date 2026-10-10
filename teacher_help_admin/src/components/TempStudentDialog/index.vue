<template>
  <el-dialog v-model="visible" title="添加临时学员" width="620px" append-to-body @open="handleOpen">
    <el-alert
      type="info"
      :closable="false"
      show-icon
      class="mb12"
      :title="attended
        ? '本课次已点名：添加后直接按所选到课状态补点名，并从该学员的课程账户扣课。'
        : '临时学员只加入本节课，不加入班级；点名时与班级学员一起点名扣课。'"
    />
    <el-form ref="formRef" :model="form" :rules="rules" label-width="96px">
      <el-form-item label="学员" prop="courseAccountId">
        <el-select
          v-model="form.courseAccountId"
          filterable
          remote
          clearable
          reserve-keyword
          :remote-method="loadOptions"
          :loading="optionLoading"
          placeholder="输入学员姓名/手机号搜索（需持有本课程有效课程账户）"
          style="width: 100%"
        >
          <el-option
            v-for="item in options"
            :key="item.courseAccountId"
            :label="`${item.studentName}（${item.phone || '-'}）剩余${item.remainingQuantity ?? 0}${item.unit || ''}`"
            :value="item.courseAccountId"
          />
        </el-select>
      </el-form-item>
      <template v-if="attended">
        <el-form-item label="到课状态" prop="status">
          <el-radio-group v-model="form.status" @change="handleStatusChange">
            <el-radio-button :label="1">到课</el-radio-button>
            <el-radio-button :label="2">迟到</el-radio-button>
            <el-radio-button :label="3">请假</el-radio-button>
            <el-radio-button :label="4">未到</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="扣除额度">
          <el-input-number v-model="form.deductQuantity" :min="0" :max="99" :disabled="![1, 2].includes(form.status)" />
          <span class="tip">请假/未到不扣课（已通过且标记扣课时的请假单除外，由后端判定）</span>
        </el-form-item>
      </template>
      <el-form-item label="备注">
        <el-input v-model="form.remark" maxlength="200" show-word-limit />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, getCurrentInstance, reactive, ref } from 'vue'
import { addTempStudent, listTempStudentOptions } from '@/api/teach/lesson'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  eventId: { type: [Number, String], default: null },
  attended: { type: Boolean, default: false }
})
const emit = defineEmits(['update:modelValue', 'success'])
const { proxy } = getCurrentInstance()

const visible = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value)
})
const formRef = ref(null)
const options = ref([])
const optionLoading = ref(false)
const submitting = ref(false)
const form = reactive({ courseAccountId: null, status: 1, deductQuantity: 1, remark: '' })
const rules = {
  courseAccountId: [{ required: true, message: '请选择学员', trigger: 'change' }],
  status: [{ required: true, message: '请选择到课状态', trigger: 'change' }]
}

function handleOpen() {
  Object.assign(form, { courseAccountId: null, status: 1, deductQuantity: 1, remark: '' })
  loadOptions('')
}

async function loadOptions(keyword) {
  if (!props.eventId) return
  optionLoading.value = true
  try {
    const response = await listTempStudentOptions({ eventId: props.eventId, keyword: keyword || undefined })
    options.value = response.data || []
  } finally {
    optionLoading.value = false
  }
}

function handleStatusChange(status) {
  form.deductQuantity = [1, 2].includes(status) ? 1 : 0
}

function submit() {
  formRef.value.validate(async valid => {
    if (!valid) return
    const option = options.value.find(item => item.courseAccountId === form.courseAccountId)
    if (!option) return
    submitting.value = true
    try {
      const payload = {
        eventId: props.eventId,
        studentId: option.studentId,
        courseAccountId: option.courseAccountId,
        remark: form.remark
      }
      if (props.attended) {
        payload.status = form.status
        payload.deductQuantity = form.deductQuantity || 0
      }
      const response = await addTempStudent(payload)
      proxy.$modal.msgSuccess(response.msg || '添加成功')
      visible.value = false
      emit('success')
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style scoped>
.mb12 {
  margin-bottom: 12px;
}

.tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}
</style>
