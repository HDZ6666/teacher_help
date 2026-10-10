<template>
  <el-dialog :model-value="modelValue" :title="isLock ? '解除锁场' : '取消预订'" width="460px" append-to-body @update:model-value="val => emit('update:modelValue', val)" @open="init">
    <el-form ref="formRef" :model="form" label-width="90px">
      <el-form-item label="场次">{{ booking.courtName }} {{ booking.bookingDate }} {{ booking.startTime }}-{{ booking.endTime }}</el-form-item>
      <template v-if="!isLock">
        <el-form-item label="实收金额">{{ paidAmount }} 元（{{ booking.payStatusName || '-' }}）</el-form-item>
        <el-form-item label="退款金额">
          <el-input-number v-model="form.refundAmount" :min="0" :max="Number(paidAmount)" :precision="2" :disabled="booking.payStatus !== 1" controls-position="right" />
          <span class="form-tip">{{ booking.payStatus === 1 ? '不能超过实收金额' : '未付款，无需退款' }}</span>
        </el-form-item>
      </template>
      <el-form-item :label="isLock ? '解除原因' : '取消原因'">
        <el-input v-model="form.cancelReason" type="textarea" :rows="3" maxlength="255" show-word-limit />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="emit('update:modelValue', false)">取 消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">确 定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, getCurrentInstance, ref } from 'vue'
import { cancelBooking } from '@/api/teach/venue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  booking: { type: Object, default: () => ({}) }
})
const emit = defineEmits(['update:modelValue', 'success'])
const { proxy } = getCurrentInstance()

const form = ref({ refundAmount: 0, cancelReason: '' })
const submitting = ref(false)
const isLock = computed(() => props.booking.bookingType === 'lock')
const paidAmount = computed(() => (Number(props.booking.amount || 0) - Number(props.booking.discountAmount || 0)).toFixed(2))

function init() {
  form.value = { refundAmount: 0, cancelReason: '' }
}

async function submit() {
  submitting.value = true
  try {
    await cancelBooking({ id: props.booking.id, refundAmount: form.value.refundAmount || 0, cancelReason: form.value.cancelReason })
    proxy.$modal.msgSuccess(isLock.value ? '已解除锁场' : '取消成功')
    emit('update:modelValue', false)
    emit('success')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.form-tip {
  margin-left: 8px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
</style>
