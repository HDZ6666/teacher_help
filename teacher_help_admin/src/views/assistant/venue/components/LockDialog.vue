<template>
  <el-dialog :model-value="modelValue" title="锁场" width="600px" append-to-body @update:model-value="val => emit('update:modelValue', val)" @open="init">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="场地" prop="courtIds">
        <el-select v-model="form.courtIds" multiple style="width: 100%" placeholder="可多选">
          <el-option v-for="court in courts" :key="court.courtId" :label="court.courtName" :value="court.courtId" />
        </el-select>
      </el-form-item>
      <el-form-item label="时间" required>
        <el-time-select v-model="form.startTime" start="00:00" step="00:30" end="23:30" :clearable="false" style="width: 120px" />
        <span class="range-sep">至</span>
        <el-time-select v-model="form.endTime" start="00:30" step="00:30" end="24:00" :clearable="false" style="width: 120px" />
      </el-form-item>
      <el-form-item label="日期范围" prop="dateRange">
        <el-date-picker v-model="form.dateRange" type="daterange" value-format="YYYY-MM-DD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" style="width: 100%" />
      </el-form-item>
      <el-form-item label="重复">
        <el-checkbox-group v-model="form.weekDays">
          <el-checkbox v-for="week in WEEK_OPTIONS" :key="week.value" :value="week.value">{{ week.label }}</el-checkbox>
        </el-checkbox-group>
        <div class="form-tip">不选表示日期范围内每天；选择后只锁定所选星期</div>
      </el-form-item>
      <el-form-item label="锁场原因">
        <el-input v-model="form.cancelReason" maxlength="255" placeholder="如 赛事包场 / 场地维护" />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" maxlength="500" />
      </el-form-item>
      <el-alert type="info" :closable="false" show-icon :title="`预计生成 ${estimateCount} 条锁场记录；任一场次已被预订或锁定时整批不生效`" />
    </el-form>
    <template #footer>
      <el-button @click="emit('update:modelValue', false)">取 消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">确认锁场</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, getCurrentInstance, ref } from 'vue'
import { lockCourt } from '@/api/teach/venue'
import { WEEK_OPTIONS } from '../utils'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  courts: { type: Array, default: () => [] },
  preset: { type: Object, default: () => ({}) }
})
const emit = defineEmits(['update:modelValue', 'success'])
const { proxy } = getCurrentInstance()

const form = ref({ courtIds: [], weekDays: [], dateRange: [] })
const submitting = ref(false)
const rules = {
  courtIds: [{ type: 'array', required: true, min: 1, message: '请选择场地', trigger: 'change' }],
  dateRange: [{ type: 'array', required: true, len: 2, message: '请选择日期范围', trigger: 'change' }]
}

const estimateCount = computed(() => {
  const [start, end] = form.value.dateRange || []
  if (!start || !end) return 0
  let count = 0
  const current = new Date(`${start}T00:00:00`)
  const last = new Date(`${end}T00:00:00`)
  while (current <= last && count < 10000) {
    const weekDay = current.getDay() === 0 ? 7 : current.getDay()
    if (!form.value.weekDays.length || form.value.weekDays.includes(weekDay)) count++
    current.setDate(current.getDate() + 1)
  }
  return count * (form.value.courtIds?.length || 0)
})

function init() {
  form.value = {
    courtIds: props.preset.courtIds || [],
    startTime: props.preset.startTime || '09:00',
    endTime: props.preset.endTime || '10:00',
    dateRange: props.preset.bookingDate ? [props.preset.bookingDate, props.preset.bookingDate] : [],
    weekDays: [],
    cancelReason: '',
    remark: ''
  }
  proxy.resetForm('formRef')
}

function submit() {
  proxy.$refs.formRef.validate(async valid => {
    if (!valid) return
    if (form.value.startTime >= form.value.endTime) {
      proxy.$modal.msgError('结束时间必须晚于开始时间')
      return
    }
    const [bookingDate, endDate] = form.value.dateRange
    submitting.value = true
    try {
      const res = await lockCourt({
        courtId: form.value.courtIds[0],
        courtIds: form.value.courtIds,
        bookingDate,
        endDate,
        weekDays: form.value.weekDays.length ? form.value.weekDays : undefined,
        startTime: form.value.startTime,
        endTime: form.value.endTime,
        cancelReason: form.value.cancelReason,
        remark: form.value.remark
      })
      proxy.$modal.msgSuccess(res.msg || '锁场成功')
      emit('update:modelValue', false)
      emit('success')
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style scoped>
.range-sep {
  margin: 0 8px;
}

.form-tip {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  line-height: 18px;
}
</style>
